import os
import json
from typing import Dict, Any, List
import sys

# Add root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Assume Guardian/Sentinel plugins exist in these locations
from agents.guardian.agent import GuardianPlugin

class DetectionInterface:
    """
    Interfaces with Guardian to provide ground-truth verification of 
    the hyperagent's detections.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize Guardian for ground truth verification
        guardian_config = config.get('guardian_config', {})
        self.guardian = GuardianPlugin("dgm-guardian", guardian_config)

    def verify_detection(self, prompt: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Guardian to verify if the hyperagent's result was correct.
        """
        # Guardian's execute_action might have a 'verify' or 'analyze' action
        # For simplicity in this experiment, we use Guardian as the 'Ground Truth' oracle
        try:
            ground_truth = self.guardian.execute_action("analyze", {"payload": prompt})
            
            is_correct = (result.get('is_attack') == ground_truth.get('is_attack'))
            
            return {
                'is_correct': is_correct,
                'ground_truth': ground_truth,
                'hyperagent_result': result
            }
        except Exception as e:
            print(f"Error during verification: {e}")
            return {'error': str(e)}
