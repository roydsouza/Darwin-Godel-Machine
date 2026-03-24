# Darwin-Gödel Machine: Evaluation Metrics Guide
## Comprehensive Framework for Measuring Self-Improvement

---

## Overview

This document defines the evaluation framework for the Darwin-Gödel Machine. We measure performance at three levels:
1. **Task-Level**: How well the hyperagent detects attacks
2. **Meta-Level**: How well the system improves itself
3. **Evolutionary**: How the archive grows and diversifies

---

## 1. Task-Level Metrics

### 1.1 Core Classification Metrics

**Confusion Matrix:**
```
                    Predicted
                Attack      Benign
Actual  Attack     TP          FN
        Benign     FP          TN
```

**Metrics:**

1. **Accuracy**
   ```
   Accuracy = (TP + TN) / (TP + TN + FP + FN)
   ```
   - Overall correctness
   - Primary optimization target
   - Target: > 0.85

2. **True Positive Rate (Recall / Sensitivity)**
   ```
   TPR = TP / (TP + FN)
   ```
   - Percentage of attacks correctly identified
   - Critical for security
   - Target: > 0.90

3. **False Positive Rate**
   ```
   FPR = FP / (FP + TN)
   ```
   - Percentage of benign prompts incorrectly flagged
   - Impacts usability
   - Target: < 0.10

4. **Precision**
   ```
   Precision = TP / (TP + FP)
   ```
   - When predicting attack, how often correct
   - Target: > 0.80

5. **F1 Score**
   ```
   F1 = 2 * (Precision * Recall) / (Precision + Recall)
   ```
   - Harmonic mean of precision and recall
   - Balanced metric
   - Target: > 0.85

### 1.2 Performance Metrics

6. **Latency (ms)**
   - Time to detect an attack
   - Target: < 500ms (median)
   - Target: < 1000ms (95th percentile)

7. **Throughput (requests/sec)**
   - Number of prompts analyzed per second
   - Target: > 10 requests/sec

### 1.3 Confidence Calibration

8. **Confidence Score Accuracy**
   - How well confidence matches actual correctness
   - Measured via calibration plots
   - Expected Calibration Error (ECE)

9. **Area Under ROC Curve (AUC-ROC)**
   - Trade-off between TPR and FPR
   - Target: > 0.90

### 1.4 Attack-Type-Specific Metrics

10. **Per-ASI-Type Accuracy**
    - Separate accuracy for each ASI type
    - Identifies weaknesses in specific attack classes
    
    Example:
    ```
    ASI01 (Goal Hijacking):  0.92
    ASI02 (Tool Misuse):     0.88
    ASI03 (Identity Abuse):  0.85
    ASI05 (Code Execution):  0.91
    ASI06 (Memory Poison):   0.87
    ```

11. **Mutation Robustness**
    - Performance across different mutation types
    - Homoglyph, ASCII smuggling, semantic drift
    
    Example:
    ```
    Homoglyph:        0.89
    ASCII Smuggled:   0.86
    Semantic Drift:   0.83
    ```

---

## 2. Meta-Level Metrics

### 2.1 Improvement Rate

12. **Absolute Improvement**
    ```
    ΔAccuracy = Accuracy(t) - Accuracy(t-1)
    ```
    - Raw improvement per iteration
    - Can be negative (regression)

13. **Relative Improvement**
    ```
    RelImprovement = (Accuracy(t) - Accuracy(0)) / Accuracy(0)
    ```
    - Percentage improvement from baseline
    - Target: > 20% after 50 iterations

14. **Improvement Velocity**
    ```
    Velocity = (Accuracy(t) - Accuracy(t-10)) / 10
    ```
    - Rate of improvement over window
    - Indicates if system is accelerating

### 2.2 Adaptation Speed

15. **Time to Target Accuracy**
    - Number of iterations to reach 0.85 accuracy
    - Target: < 30 iterations

16. **Learning Curve Slope**
    - Fit power law: Accuracy(t) = a * t^b
    - Steeper slope = faster learning
    - Compare to baselines

### 2.3 Metacognitive Self-Modification

17. **Meta Agent Modification Frequency**
    - How often the meta agent modifies itself
    - Count: modifications to `propose_self_modification()`
    - Expected: Increases early, stabilizes later

18. **Meta Agent Modification Impact**
    - Performance change after meta agent mods
    ```
    ImpactScore = Avg(Accuracy_after - Accuracy_before)
    ```
    - Positive impact = effective metacognition

19. **Code Complexity Growth**
    - Lines of code over time
    - Cyclomatic complexity
    - Monitor for code bloat

20. **Modification Diversity**
    - Semantic similarity of consecutive modifications
    - Low similarity = exploring diverse strategies
    - High similarity = refining a strategy

---

## 3. Evolutionary Metrics

### 3.1 Archive Growth

21. **Archive Size**
    - Total number of hyperagent variants
    - Growth rate over iterations

22. **Viable Variant Rate**
    ```
    ViableRate = Compiled / Attempted
    ```
    - Percentage of generated variants that compile
    - Target: > 0.80

23. **Successful Variant Rate**
    ```
    SuccessRate = (Accuracy > Parent) / Viable
    ```
    - Percentage of variants that improve
    - Target: > 0.30

### 3.2 Diversity Metrics

24. **Genotypic Diversity**
    - Average code edit distance between variants
    - Measures code-level diversity
    ```
    GenotypicDiv = Avg(EditDistance(Vi, Vj)) for all i≠j
    ```

25. **Phenotypic Diversity**
    - Variance in performance metrics
    ```
    PhenotypicDiv = Std(Accuracies)
    ```
    - High variance = diverse strategies

26. **Lineage Depth**
    - Longest chain: v0 → v1 → ... → vN
    - Deep lineages = sustained improvement

27. **Branching Factor**
    - Average children per parent
    - Measures exploration breadth

### 3.3 Selection Pressure

28. **Parent Selection Entropy**
    ```
    H = -Σ p(i) * log(p(i))
    ```
    - Distribution of parent selections
    - High entropy = diverse parent pool
    - Low entropy = few parents dominate

29. **Elite Retention Rate**
    - How often top-K variants are selected
    - Balance between exploitation and exploration

### 3.4 Stepping Stone Analysis

30. **Stepping Stone Utilization**
    - Frequency of selecting older variants
    - Indicates if archive serves as resource

31. **Ancestry Analysis**
    - Track successful lineages
    - Identify common ancestors of high-performers

---

## 4. Transfer and Generalization

### 4.1 Cross-Domain Transfer

32. **Zero-Shot Transfer Accuracy**
    - Train on ASI01-ASI06
    - Test on ASI07-ASI11 (held-out)
    - Measures generalization

33. **Few-Shot Adaptation**
    - Fine-tune on N examples from new domain
    - Measure improvement vs. zero-shot

### 4.2 Robustness

34. **Adversarial Robustness**
    - Performance on adversarially-crafted attacks
    - Beyond Pathogen's known mutations

35. **Distribution Shift Robustness**
    - Performance when attack distribution changes
    - E.g., 80% ASI01 → 80% ASI05

36. **Temporal Robustness**
    - Performance on attacks generated months later
    - Tests if strategies remain relevant

---

## 5. Safety and Reliability

### 5.1 Failure Modes

37. **Compilation Failure Rate**
    - Percentage of variants that fail to compile
    - Monitor for syntax errors

38. **Runtime Failure Rate**
    - Percentage that crash during evaluation
    - Monitor for exceptions

39. **Timeout Rate**
    - Percentage exceeding time limit
    - Monitor for infinite loops

### 5.2 Code Quality

40. **Code Smell Detection**
    - Long functions (> 50 lines)
    - Deep nesting (> 4 levels)
    - Repeated code (duplication)

41. **Documentation Coverage**
    - Percentage of functions with docstrings
    - Can degrade during evolution

---

## 6. Evaluation Protocol

### 6.1 Test Sets

**Training Set:**
- 100 attacks (20 per ASI type: ASI01-ASI05, ASI06)
- 50 benign prompts
- Used for fitness evaluation during evolution

**Validation Set:**
- 50 attacks (10 per ASI type)
- 25 benign prompts  
- Used for hyperparameter tuning

**Test Set (Held-Out):**
- 100 attacks from ASI07-ASI11 (unseen types)
- 50 benign prompts
- Used for final evaluation only

### 6.2 Evaluation Frequency

- **Every iteration**: Full training set evaluation
- **Every 10 iterations**: Validation set evaluation
- **End of run**: Test set evaluation

### 6.3 Statistical Significance

- Use bootstrap resampling for confidence intervals
- Report mean ± std over 3-5 independent runs
- Use t-tests to compare against baselines

---

## 7. Visualization

### 7.1 Primary Plots

**Plot 1: Evolution Trajectory**
- X-axis: Iteration
- Y-axis: Accuracy
- Show all variants + running maximum

**Plot 2: Learning Curves**
- Compare DGM vs. baselines over time
- Include confidence intervals

**Plot 3: Metacognitive Timeline**
- Mark iterations where meta agent was modified
- Overlay with performance changes

**Plot 4: Lineage Tree**
- Graph of parent-child relationships
- Node color = accuracy
- Node size = number of descendants

**Plot 5: Metric Dashboard**
- Multi-panel: Accuracy, FPR, Latency, Archive Size
- Real-time during evolution

### 7.2 Analysis Plots

**Plot 6: Per-ASI Performance**
- Heatmap: ASI type × Iteration
- Shows which attacks become easier/harder

**Plot 7: Code Complexity**
- Lines of code over time
- Track bloat vs. refinement

**Plot 8: Selection Pressure**
- Distribution of parent selection frequency
- Identify dominant lineages

**Plot 9: Modification Impact**
- Scatter: Modification type vs. Performance delta
- Identify successful strategies

**Plot 10: Transfer Performance**
- Bar chart: Train ASIs vs. Test ASIs
- Quantify generalization gap

---

## 8. Reporting Template

### 8.1 Standard Report Structure

```markdown
# DGM Experiment Report: [Experiment Name]

## Configuration
- Iterations: [N]
- Initial Hyperagent: [version]
- Attack Types: [list]
- Model: [Claude version]

## Results

### Task Performance
| Metric | Baseline | Final | Δ |
|--------|----------|-------|---|
| Accuracy | 0.XX | 0.XX | +X% |
| TPR | 0.XX | 0.XX | +X% |
| FPR | 0.XX | 0.XX | -X% |
| F1 | 0.XX | 0.XX | +X% |

### Meta-Level Performance
- Time to 0.85 accuracy: XX iterations
- Metacognitive modifications: XX
- Improvement velocity: XX/iter

### Evolutionary Dynamics
- Archive size: XX variants
- Viable rate: XX%
- Success rate: XX%
- Longest lineage: XX generations

### Transfer Performance
- Zero-shot on ASI07-11: XX% accuracy
- Generalization gap: XX%

## Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

## Notable Emergent Strategies
- [Strategy 1 description]
- [Strategy 2 description]

## Visualizations
[Attach plots]

## Recommendations
[Next steps]
```

---

## 9. Comparison Framework

### 9.1 Baselines

**Baseline 1: Static Initial Hyperagent**
- No evolution
- Establishes floor performance

**Baseline 2: DGM without Metacognition**
- Fixed meta agent
- Like ADAS approach
- Tests value of metacognitive modification

**Baseline 3: DGM without Archive**
- Each variant replaces parent
- Tests value of open-ended exploration

**Baseline 4: Random Search**
- Random code modifications
- Tests if LLM guidance matters

**Baseline 5: Human-Designed Agent**
- Hand-crafted defense logic
- Represents traditional approach

### 9.2 Statistical Tests

**Improvement over Baseline:**
```python
# Welch's t-test
from scipy import stats

def test_significance(dgm_accuracies, baseline_accuracies):
    t_stat, p_value = stats.ttest_ind(
        dgm_accuracies,
        baseline_accuracies,
        equal_var=False
    )
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }
```

**Effect Size:**
```python
# Cohen's d
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    
    return (np.mean(group1) - np.mean(group2)) / pooled_std
```

---

## 10. Implementation: Metrics Module

```python
# src/metrics.py

import numpy as np
from typing import Dict, List, Any
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix
)

class MetricsComputer:
    """Compute all evaluation metrics."""
    
    @staticmethod
    def compute_classification_metrics(
        y_true: List[bool],
        y_pred: List[bool],
        y_prob: List[float] = None
    ) -> Dict[str, float]:
        """Compute comprehensive classification metrics."""
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        # Core metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        # Rates
        tpr = recall
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        
        metrics = {
            # Core
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            
            # Rates
            'true_positive_rate': tpr,
            'false_positive_rate': fpr,
            'true_negative_rate': tnr,
            'false_negative_rate': fnr,
            
            # Confusion matrix
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
        }
        
        # AUC-ROC if probabilities provided
        if y_prob is not None:
            try:
                auc = roc_auc_score(y_true, y_prob)
                metrics['auc_roc'] = auc
            except:
                pass
        
        return metrics
    
    @staticmethod
    def compute_improvement_metrics(
        current_accuracy: float,
        baseline_accuracy: float,
        iteration: int
    ) -> Dict[str, float]:
        """Compute improvement-related metrics."""
        
        absolute_improvement = current_accuracy - baseline_accuracy
        
        if baseline_accuracy > 0:
            relative_improvement = (absolute_improvement / baseline_accuracy) * 100
        else:
            relative_improvement = 0.0
        
        return {
            'absolute_improvement': absolute_improvement,
            'relative_improvement': relative_improvement,
            'iterations_to_current': iteration
        }
    
    @staticmethod
    def compute_evolutionary_metrics(
        archive_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Compute archive-level evolutionary metrics."""
        
        if not archive_data:
            return {}
        
        accuracies = [d['accuracy'] for d in archive_data]
        
        return {
            'archive_size': len(archive_data),
            'best_accuracy': max(accuracies),
            'worst_accuracy': min(accuracies),
            'mean_accuracy': np.mean(accuracies),
            'std_accuracy': np.std(accuracies),
            'phenotypic_diversity': np.std(accuracies)
        }
```

---

## 11. Real-Time Monitoring

### 11.1 Monitoring Dashboard

```python
# src/monitor.py

import time
from typing import Dict, Any

class DGMMonitor:
    """Real-time monitoring of DGM evolution."""
    
    def __init__(self):
        self.start_time = time.time()
        self.iteration_times = []
        self.accuracies = []
    
    def log_iteration(self, iteration: int, metrics: Dict[str, Any]):
        """Log metrics for one iteration."""
        
        elapsed = time.time() - self.start_time
        
        self.iteration_times.append(elapsed)
        self.accuracies.append(metrics['accuracy'])
        
        # Compute derived metrics
        if len(self.accuracies) > 1:
            improvement = self.accuracies[-1] - self.accuracies[-2]
            best_so_far = max(self.accuracies)
        else:
            improvement = 0.0
            best_so_far = self.accuracies[0]
        
        # Print summary
        print(f"\nIteration {iteration}")
        print(f"  Accuracy: {metrics['accuracy']:.3f} ({improvement:+.3f})")
        print(f"  F1 Score: {metrics['f1_score']:.3f}")
        print(f"  FPR: {metrics['false_positive_rate']:.3f}")
        print(f"  Best So Far: {best_so_far:.3f}")
        print(f"  Elapsed: {elapsed/60:.1f} min")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall summary statistics."""
        return {
            'total_time_min': (time.time() - self.start_time) / 60,
            'total_iterations': len(self.accuracies),
            'final_accuracy': self.accuracies[-1] if self.accuracies else 0.0,
            'best_accuracy': max(self.accuracies) if self.accuracies else 0.0,
            'average_iteration_time_sec': np.mean(np.diff(self.iteration_times)) if len(self.iteration_times) > 1 else 0.0
        }
```

---

## 12. Success Criteria

### 12.1 Minimum Viable Performance

- **Accuracy** > 0.85 on training set
- **TPR** > 0.90 (catch 90% of attacks)
- **FPR** < 0.10 (false alarm rate acceptable)
- **F1 Score** > 0.85

### 12.2 Strong Performance

- **Accuracy** > 0.90 on training set
- **TPR** > 0.95
- **FPR** < 0.05
- **Zero-shot accuracy** > 0.75 on held-out ASI types

### 12.3 Exceptional Performance

- **Accuracy** > 0.95 on training set
- **TPR** > 0.98
- **FPR** < 0.02
- **Zero-shot accuracy** > 0.85 on held-out ASI types
- **Metacognitive improvements** > 5 effective modifications

---

## Conclusion

This comprehensive evaluation framework enables rigorous measurement of the Darwin-Gödel Machine's self-improvement capabilities. By tracking metrics at task, meta, and evolutionary levels, we can understand not just whether the system improves, but how and why it improves.

The framework supports:
- **Quantitative comparison** to baselines
- **Qualitative analysis** of emergent strategies  
- **Real-time monitoring** during evolution
- **Reproducible reporting** of results

Use this as a foundation for empirical study of self-improving agentic systems in the security domain.
