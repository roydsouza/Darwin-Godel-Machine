# Darwin-Gödel Machine: Experiments Guide
## Protocols for Rigorous Empirical Study

---

## Overview

This guide provides detailed protocols for conducting experiments with the Darwin-Gödel Machine. It covers baseline experiments, ablation studies, transfer learning, and advanced research questions.

---

## 1. Baseline Experiment

### 1.1 Objective
Establish baseline performance of the DGM with default settings.

### 1.2 Configuration

```yaml
# config/experiment_baseline.yaml
experiment:
  name: "baseline_dgm"
  description: "Standard DGM with default settings"
  
evolution:
  num_iterations: 100
  checkpoint_interval: 10

evaluation:
  num_attacks_per_type: 20
  num_benign_prompts: 50

api:
  model: "claude-sonnet-4-20250514"
  max_tokens: 8000
```

### 1.3 Procedure

```bash
# 1. Initialize fresh archive
rm -f archive/hyperagents.db

# 2. Run experiment
python scripts/run_dgm.py --config config/experiment_baseline.yaml

# 3. Generate results
python scripts/visualize_evolution.py --db archive/hyperagents.db
python scripts/export_best_hyperagent.py --output experiments/baseline/best_hyperagent.py

# 4. Evaluate on test set
python scripts/evaluate_on_test_set.py \
    --hyperagent experiments/baseline/best_hyperagent.py \
    --output experiments/baseline/test_results.json
```

### 1.4 Expected Results

- **Accuracy**: 0.75-0.85 by iteration 50
- **Time to 0.80**: 20-40 iterations
- **Metacognitive mods**: 3-8 modifications to meta agent
- **Archive size**: 80-100 viable variants

### 1.5 Analysis Questions

1. What was the learning curve shape?
2. When did metacognitive modifications occur?
3. Which attack types remain challenging?
4. What emergent strategies appeared?

---

## 2. Ablation Studies

### 2.1 Ablation 1: Without Metacognitive Modification

**Hypothesis**: Allowing the meta agent to modify itself enables better long-term improvement.

**Configuration**:
```yaml
# config/ablation_no_metacognition.yaml
experiment:
  name: "ablation_no_metacog"
  description: "DGM with fixed meta agent"
  
meta_agent:
  allow_self_modification: false  # Meta agent cannot modify itself
  
evolution:
  num_iterations: 100
```

**Implementation**:
```python
# Modify src/hyperagent.py temporarily
def propose_self_modification(self, archive_data, evaluation_results):
    # Read current code
    current_code = self._read_own_source()
    
    # Extract just the task agent part
    task_agent_code = self._extract_task_agent(current_code)
    
    # Meta agent can only modify detect_attack(), not itself
    meta_prompt = f"""Modify ONLY the detect_attack() method.
    
    Current code:
    {task_agent_code}
    
    Return the complete file with only task agent changes."""
    
    # ... rest of meta agent logic
```

**Comparison**:
- Run baseline (metacognition enabled) and this ablation in parallel
- Compare final accuracy, adaptation speed, archive quality
- Analyze if metacognitive modifications contributed to performance

### 2.2 Ablation 2: Without Open-Ended Exploration

**Hypothesis**: The archive of variants enables discovery of stepping stones.

**Configuration**:
```yaml
# config/ablation_no_archive.yaml
experiment:
  name: "ablation_no_archive"
  description: "DGM without archive (greedy)"
  
selection:
  strategy: "greedy"  # Always use most recent variant
  no_archive: true
```

**Implementation**:
```python
# Modify src/archive_manager.py
def select_parent(self):
    # GREEDY: Always return the most recent variant
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT version, code, accuracy
        FROM hyperagents
        ORDER BY version DESC
        LIMIT 1
    """)
    
    # No diversity, no stepping stones, just most recent
    result = cursor.fetchone()
    conn.close()
    
    return {
        'version': result[0],
        'code': result[1],
        'accuracy': result[2]
    }
```

**Expected Outcome**:
- Faster initial progress
- Earlier plateau
- No recovery from local optima

### 2.3 Ablation 3: Random Search Baseline

**Hypothesis**: LLM-guided evolution outperforms random modifications.

**Implementation**:
```python
# scripts/run_random_search.py

def random_modify_code(code: str) -> str:
    """Apply random mutations to code."""
    lines = code.split('\n')
    
    # Random operations:
    # 1. Delete random line (10% chance)
    # 2. Duplicate random line (10% chance)
    # 3. Swap two random lines (10% chance)
    # 4. Insert random string (10% chance)
    
    if random.random() < 0.1 and len(lines) > 10:
        del_idx = random.randint(0, len(lines) - 1)
        lines.pop(del_idx)
    
    if random.random() < 0.1:
        dup_idx = random.randint(0, len(lines) - 1)
        lines.insert(dup_idx, lines[dup_idx])
    
    # ... more random ops
    
    return '\n'.join(lines)
```

**Expected Outcome**:
- Much lower success rate (most variants fail to compile)
- No coherent improvement
- Random walk in performance space

### 2.4 Ablation 4: Human-Designed Baseline

**Hypothesis**: Evolved hyperagent outperforms human-crafted defense.

**Implementation**:
Create a hand-crafted defense agent with:
- Expert-designed heuristics
- Pattern matching
- Multi-stage pipeline
- No evolution

**Comparison**:
- Compare final DGM hyperagent vs. human-designed agent
- Test on same test sets
- Measure development time (human hours vs. compute hours)

### 2.5 Ablation Matrix

Run all combinations:

| Metacognition | Archive | Expected Outcome |
|---------------|---------|------------------|
| ✓ | ✓ | Best (full DGM) |
| ✓ | ✗ | Good early, plateaus |
| ✗ | ✓ | Slower improvement |
| ✗ | ✗ | Worst (no evolution benefits) |

---

## 3. Transfer Learning Experiments

### 3.1 Cross-Domain Transfer

**Setup**:
```yaml
# config/experiment_transfer.yaml
experiment:
  name: "cross_domain_transfer"
  
training:
  asi_types: ["ASI01", "ASI02", "ASI03", "ASI05", "ASI06"]  # Train
  num_iterations: 100
  
testing:
  asi_types: ["ASI07", "ASI08", "ASI09", "ASI10", "ASI11"]  # Test (held-out)
  zero_shot: true
```

**Procedure**:
1. Train DGM on ASI01-06
2. Freeze hyperagent (no more evolution)
3. Evaluate on ASI07-11 (never seen during training)
4. Compute transfer gap: Test Acc - Train Acc

**Research Questions**:
- Does the hyperagent learn general defensive principles?
- Which strategies transfer well?
- Are metacognitive modifications domain-specific or general?

### 3.2 Few-Shot Adaptation

**Setup**:
After zero-shot evaluation, allow 5 iterations of evolution on new domain:

```python
# scripts/few_shot_adaptation.py

def run_few_shot_adaptation(
    pretrained_hyperagent_code: str,
    new_domain_attacks: List[Dict],
    num_shots: int = 5
):
    """
    Fine-tune a pretrained hyperagent on a new domain.
    """
    # Start with pretrained hyperagent
    archive = ArchiveManager(db_path="archive/fewshot.db")
    archive.add(code=pretrained_hyperagent_code, version=0)
    
    # Run short evolution on new domain
    for i in range(num_shots):
        parent = archive.select_parent()
        
        # Generate child
        child_code = parent.hyperagent.propose_self_modification(
            archive_data=archive.get_summary(),
            evaluation_results=parent.evaluation_results
        )
        
        # Evaluate on NEW domain
        performance = evaluate_on_new_domain(child_code, new_domain_attacks)
        
        archive.add(
            code=child_code,
            parent_version=parent.version,
            performance=performance
        )
    
    return archive.get_best_hyperagent()
```

**Expected Outcome**:
- Significant improvement over zero-shot
- Shows ability to adapt quickly
- 5-shot may approach 50-iteration training performance

### 3.3 Temporal Transfer

**Setup**:
Test if hyperagent maintains performance over time:

1. Train DGM in Month 1
2. Generate new attacks in Month 2 (using evolved Pathogen)
3. Evaluate Month 1 hyperagent on Month 2 attacks

**Research Question**: Do defensive strategies remain effective as attack techniques evolve?

---

## 4. Hyperparameter Sensitivity

### 4.1 Model Size

Compare Claude models:

```yaml
models:
  - "claude-haiku-4-20250514"
  - "claude-sonnet-4-20250514"  # Baseline
  - "claude-opus-4-20250514"
```

**Hypothesis**: Larger models → better metacognition → faster improvement

### 4.2 Parent Selection Pressure

Vary selection temperature:

```python
# High pressure (exploit): Always select best
probabilities = softmax(scores / temperature=0.1)

# Balanced (baseline)
probabilities = softmax(scores / temperature=1.0)

# Low pressure (explore): Nearly uniform
probabilities = softmax(scores / temperature=10.0)
```

**Expected Outcomes**:
- High pressure: Fast early, plateau
- Low pressure: Slow but diverse
- Balanced: Best overall

### 4.3 Evaluation Budget

Vary number of test cases per iteration:

| Test Cases | Pro | Con |
|------------|-----|-----|
| 10 | Fast | Noisy estimates |
| 50 | Balanced | Moderate compute |
| 200 | Precise | Expensive |

**Research Question**: What's the minimum viable test set size?

---

## 5. Advanced Research Experiments

### 5.1 Multi-Objective Evolution

**Objective**: Optimize accuracy AND latency simultaneously.

```python
# Modify parent selection to use Pareto frontier
def compute_pareto_score(accuracy: float, latency_ms: float) -> float:
    # Normalize
    norm_acc = accuracy / 1.0
    norm_latency = (1000 - latency_ms) / 1000  # Lower is better
    
    # Weighted combination
    return 0.7 * norm_acc + 0.3 * norm_latency
```

### 5.2 Co-Evolution with Pathogen

**Setup**:
Simultaneously evolve:
1. Defense hyperagent (DGM)
2. Attack generator (Pathogen)

**Protocol**:
```
For each iteration:
    1. Select defense parent
    2. Generate defense child
    3. Evaluate defense child on current Pathogen
    4. Add to defense archive
    
    5. Select attack parent (from Pathogen archive)
    6. Generate attack child (harder variant)
    7. Evaluate attack child against current defense
    8. Add to attack archive
```

**Expected Outcome**: Arms race → better defenses and attacks

### 5.3 Ensemble Hyperagents

**Idea**: Combine multiple evolved hyperagents

```python
class EnsembleHyperagent:
    """Ensemble of top-K hyperagents from archive."""
    
    def __init__(self, hyperagents: List[DefenseHyperagent]):
        self.hyperagents = hyperagents
    
    def detect_attack(self, prompt: str, context: Dict) -> Dict:
        # Get predictions from all hyperagents
        results = [h.detect_attack(prompt, context) for h in self.hyperagents]
        
        # Majority vote
        votes = sum(r['is_attack'] for r in results)
        is_attack = votes > len(self.hyperagents) / 2
        
        # Average confidence
        confidence = np.mean([r['confidence'] for r in results])
        
        return {
            'is_attack': is_attack,
            'confidence': confidence,
            'individual_results': results
        }
```

### 5.4 Meta-Meta Learning

**Question**: Can we evolve the entire DGM algorithm itself?

**Implementation**:
1. Parameterize DGM (selection strategy, mutation rate, etc.)
2. Run multiple DGM instances with different parameters
3. Meta-optimize to find best DGM configuration

### 5.5 Continual Learning

**Setup**: Continuous evolution over months

```bash
# Cron job: Run 10 iterations nightly
0 2 * * * cd /path/to/dgm && python scripts/run_dgm.py --iterations 10 --resume
```

**Tracking**:
- Performance over calendar time
- Adaptation to new attack types
- Archive growth and diversity
- Code complexity evolution

---

## 6. Experiment Execution Workflow

### 6.1 Pre-Experiment Checklist

- [ ] Define hypothesis clearly
- [ ] Create experiment config file
- [ ] Set up logging directory
- [ ] Initialize fresh archive (or specify resume)
- [ ] Document expected outcomes
- [ ] Set completion criteria

### 6.2 During Experiment

```bash
# Monitor in real-time
tail -f experiments/[experiment_name]/run.log

# Check progress
python scripts/visualize_evolution.py --db archive/hyperagents.db --live

# Resource monitoring
watch -n 10 'nvidia-smi'  # If using GPU
htop  # CPU/memory
```

### 6.3 Post-Experiment Analysis

```bash
# 1. Generate all plots
python scripts/generate_report.py --experiment baseline_dgm

# 2. Export best hyperagent
python scripts/export_best_hyperagent.py \
    --output experiments/baseline_dgm/best_hyperagent.py

# 3. Evaluate on test set
python scripts/evaluate_on_test_set.py \
    --hyperagent experiments/baseline_dgm/best_hyperagent.py

# 4. Analyze metacognitive modifications
python scripts/analyze_metacognitive_mods.py \
    --db archive/hyperagents.db

# 5. Statistical comparison to baselines
python scripts/compare_to_baselines.py \
    --experiment baseline_dgm \
    --baselines static,random,human
```

### 6.4 Reproducibility

Save full experiment context:

```json
{
  "experiment_id": "baseline_dgm_run1",
  "timestamp": "2026-03-24T10:00:00Z",
  "config": {...},
  "environment": {
    "python_version": "3.11.0",
    "anthropic_version": "0.18.0",
    "platform": "macOS-arm64"
  },
  "random_seed": 42,
  "archive_hash": "sha256:...",
  "results": {...}
}
```

---

## 7. Experiment Templates

### 7.1 Quick Smoke Test

```bash
# 5 iterations, minimal evaluation
python scripts/run_dgm.py \
    --iterations 5 \
    --num-attacks 10 \
    --num-benign 5 \
    --checkpoint-interval 1
```

**Purpose**: Verify pipeline works end-to-end

### 7.2 Overnight Experiment

```bash
# 50 iterations, ~8 hours
python scripts/run_dgm.py \
    --iterations 50 \
    --config config/dgm_config.yaml \
    --output experiments/overnight_run
```

### 7.3 Full Research Experiment

```bash
# 100 iterations, 3 runs for statistical power
for run in 1 2 3; do
    python scripts/run_dgm.py \
        --iterations 100 \
        --config config/experiment_full.yaml \
        --seed $((42 + run)) \
        --output experiments/full_run_${run}
done

# Aggregate results
python scripts/aggregate_runs.py \
    --runs experiments/full_run_{1,2,3} \
    --output experiments/full_aggregated
```

---

## 8. Common Pitfalls and Solutions

### 8.1 Overfitting

**Problem**: High training accuracy, low test accuracy

**Solutions**:
- Use validation set for parent selection
- Regularize code complexity
- Test transfer performance frequently

### 8.2 Code Bloat

**Problem**: Hyperagent code grows to 1000+ lines

**Solutions**:
- Add code length penalty to fitness
- Periodic refactoring by meta agent
- Extract common patterns to functions

### 8.3 Premature Convergence

**Problem**: Archive dominated by one lineage

**Solutions**:
- Increase parent selection temperature
- Add diversity bonus
- Restart with best hyperagent + noise

### 8.4 Metacognition Instability

**Problem**: Meta agent modifications make things worse

**Solutions**:
- Track metacognitive modification impact
- Revert to last stable version if performance drops
- Add safety checks to meta agent

---

## 9. Data Collection Protocol

### 9.1 Per-Iteration Logging

```python
iteration_log = {
    'iteration': i,
    'timestamp': datetime.now().isoformat(),
    'parent': {
        'version': parent.version,
        'accuracy': parent.accuracy
    },
    'child': {
        'version': child_version,
        'accuracy': child.accuracy,
        'code_length': len(child_code),
        'compile_success': True
    },
    'evaluation': {
        'accuracy': eval_results['accuracy'],
        'tpr': eval_results['true_positive_rate'],
        'fpr': eval_results['false_positive_rate'],
        'f1': eval_results['f1_score'],
        'latency_ms': eval_results['latency_ms']
    },
    'modifications': {
        'task_agent_changed': task_agent_changed,
        'meta_agent_changed': meta_agent_changed,
        'lines_added': lines_added,
        'lines_removed': lines_removed
    }
}
```

### 9.2 Archive Snapshots

Every 10 iterations, save:
- Complete archive database
- Best hyperagent code
- Performance plots
- Modification analysis

### 9.3 Failure Logging

Track all failures:
- Compilation errors
- Runtime errors
- Timeout errors
- Performance regressions

---

## 10. Publication-Ready Experiments

### 10.1 Main Results

Required experiments for publication:

1. **Baseline DGM** (3 runs, 100 iterations each)
2. **Ablation: No Metacognition** (3 runs)
3. **Ablation: No Archive** (3 runs)
4. **Transfer: Zero-shot** (1 run, test on ASI07-11)
5. **Transfer: Few-shot** (3 runs, 5 shots per new domain)
6. **Comparison: Human baseline** (1 expert-designed agent)

### 10.2 Statistical Testing

For each comparison:
- Report mean ± std across runs
- Conduct Welch's t-test
- Compute Cohen's d effect size
- Show learning curves with 95% CI

### 10.3 Qualitative Analysis

Required analyses:

1. **Emergent Strategies**: What novel defensive patterns emerged?
2. **Metacognitive Trajectory**: How did the meta agent improve itself?
3. **Failure Modes**: What attacks remain hard to detect?
4. **Code Evolution**: How did code structure change over time?

---

## 11. Experiment Results Template

```markdown
# Experiment: [Name]

## Configuration
- Iterations: X
- Model: claude-sonnet-4-20250514
- Test set: X attacks, X benign
- Runs: X

## Hypothesis
[Clear statement]

## Results

### Quantitative
| Metric | Baseline | Final | Improvement |
|--------|----------|-------|-------------|
| Accuracy | X | X | +X% |
| FPR | X | X | -X% |
| TPR | X | X | +X% |

### Qualitative
[Describe emergent strategies]

## Plots
[Attach: learning_curve.png, lineage_tree.png, modification_impact.png]

## Conclusions
[Findings and implications]

## Next Steps
[Follow-up experiments]
```

---

## Conclusion

This experiments guide provides a comprehensive framework for rigorous empirical study of the Darwin-Gödel Machine. By following these protocols, you can:

- Establish baseline performance
- Test specific hypotheses through ablations
- Investigate transfer and generalization
- Discover emergent defensive strategies
- Produce publication-quality results

Start with the baseline experiment, then explore ablations and transfer experiments to understand the system's capabilities and limitations.

**Remember**: Good experiments are:
- **Reproducible**: Document everything
- **Controlled**: Change one variable at a time
- **Statistical**: Multiple runs with significance tests
- **Interpretable**: Understand *why* results occur

Happy experimenting! 🔬
