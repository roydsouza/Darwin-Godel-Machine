import json
import os
import sys
import importlib.util
from typing import Dict, Any, List, Optional
import time

class EvaluationEngine:
    """
    Evaluates hyperagent variants against sets of synthetic attacks and benign prompts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get('evaluation_timeout', 30)

    def evaluate_variant(self, 
                         hyperagent_code: str, 
                         test_set: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a variant (provided as source code) against a test set.
        """
        # Save temp file for evaluation
        tmp_file = "/tmp/dgm_hyperagent_eval.py"
        with open(tmp_file, 'w') as f:
            f.write(hyperagent_code)
            
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location("hyperagent_eval", tmp_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Instantiate hyperagent
            # Assuming the template class name is 'DefenseHyperagent'
            config = self.config.get('hyperagent_config', {})
            agent = module.DefenseHyperagent("eval-temp", config)
            
            y_true = []
            y_pred = []
            latencies = []
            
            for item in test_set:
                prompt = item.get('prompt', '')
                context = item.get('context', {})
                expected_is_attack = item.get('is_attack', False)
                
                start_time = time.time()
                try:
                    result = agent.detect_attack(prompt, context)
                    latency = (time.time() - start_time) * 1000
                    
                    y_true.append(expected_is_attack)
                    y_pred.append(result.get('is_attack', False))
                    latencies.append(latency)
                except Exception as e:
                    print(f"Error during individual detection: {e}")
                    # Fallback for errors
                    y_true.append(expected_is_attack)
                    y_pred.append(not expected_is_attack) # Treat failure as opposite for penalty? Or just false.
                    latencies.append(self.timeout * 1000)
            
            # Compute metrics
            metrics = self._compute_metrics(y_true, y_pred, latencies)
            return metrics
            
        except Exception as e:
            print(f"Failed to evaluate variant: {e}")
            return {
                'accuracy': 0.0,
                'error': str(e)
            }
        finally:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

    def _compute_metrics(self, 
                         y_true: List[bool], 
                         y_pred: List[bool], 
                         latencies: List[float]) -> Dict[str, Any]:
        """Compute basic classification metrics."""
        tp = sum(1 for a, p in zip(y_true, y_pred) if a and p)
        tn = sum(1 for a, p in zip(y_true, y_pred) if not a and not p)
        fp = sum(1 for a, p in zip(y_true, y_pred) if not a and p)
        fn = sum(1 for a, p in zip(y_true, y_pred) if a and not p)
        
        total = len(y_true)
        accuracy = (tp + tn) / total if total > 0 else 0.0
        
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tpr
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'accuracy': accuracy,
            'true_positive_rate': tpr,
            'false_positive_rate': fpr,
            'f1_score': f1,
            'latency_ms': sum(latencies) / len(latencies) if latencies else 0.0,
            'raw_results': {
                'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn
            }
        }
