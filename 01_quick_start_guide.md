# Darwin-Gödel Machine Lab - Quick Start Guide

## Welcome to Self-Evolving Defense! 🧬

This lab implements a **Darwin-Gödel Machine** following the HyperAgent Principle - a single self-referential Python program that can detect attacks AND improve itself, including improving how it improves.

---

## What You're Building

A self-improving agentic firewall defense that:
- **Task Agent**: Detects prompt injection, jailbreaks, and other ASI attacks
- **Meta Agent**: Analyzes failures and modifies the entire hyperagent (including itself)
- **Archive**: Stores evolutionary history as stepping stones
- **Integration**: Uses Tachyon Tongs' Pathogen for attacks, Sentinel/Guardian for verification

---

## Document Overview

**Start here:**
1. **darwin_godel_machine_design.md** - Comprehensive architecture and design
2. **implementation_guide.md** - Step-by-step coding instructions
3. **hyperagent_template.md** - Initial hyperagent code (the seed)

**Supporting docs:**
4. **evaluation_metrics.md** - How to measure performance
5. **experiments_guide.md** - Research protocols and ablations

---

## Quick Start (5 minutes)

### Prerequisites

```bash
# Python 3.10+
python --version

# Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# Required packages
pip install anthropic>=0.18.0 numpy>=1.24.0 pyyaml>=6.0 sqlalchemy>=2.0.0
```

### Step 1: Create Directory Structure

```bash
cd tachyon_tongs
mkdir -p ~/antigravity/tachyon_tongs/experiments/darwin_godel_machine/{src,archive,config,experiments,tests,scripts}
cd ~/antigravity/tachyon_tongs/experiments/darwin_godel_machine
```

### Step 2: Copy Initial Files

```bash
# 1. Copy hyperagent template to src/hyperagent.py
#    (from hyperagent_template.md)

# 2. Copy config to config/dgm_config.yaml
#    (from implementation_guide.md Phase 1)

# 3. Copy core modules to src/
#    - archive_manager.py
#    - evaluation_engine.py
#    - attack_interface.py
#    (all in implementation_guide.md Phase 2)

# 4. Copy main runner to scripts/run_dgm.py
#    (from implementation_guide.md Phase 2)
```

### Step 3: Test the Pipeline

```bash
# Test the initial hyperagent
python src/hyperagent.py

# Run one iteration (smoke test)
python scripts/run_dgm.py --iterations 1

# If successful, you'll see:
# - "Selected parent: v0"
# - "Child performance: accuracy: X.XXX"
# - "Added child to archive (v1)"
```

### Step 4: Run Your First Experiment

```bash
# Start with a short experiment (10 iterations, ~30 minutes)
python scripts/run_dgm.py --iterations 10

# Monitor progress in another terminal
tail -f logs/dgm_run.log

# Visualize results
python scripts/visualize_evolution.py
```

---

## Understanding the Evolution

### What Happens Each Iteration

```
1. SELECT: Choose parent from archive (weighted by accuracy)
   └─> "Selected parent: v5 (accuracy: 0.783)"

2. MODIFY: Parent's meta agent proposes improvements
   └─> "Generating child variant..."
   └─> Meta agent reads own code, analyzes failures, suggests changes

3. EVALUATE: Test child on synthetic attacks
   └─> "Evaluating child hyperagent..."
   └─> Run 100 attacks + 50 benign prompts
   └─> Measure accuracy, FPR, TPR, latency

4. ADD: Store in archive
   └─> "Added child to archive (v6)"
   └─> New variant becomes available for future parent selection

5. REPEAT: Next iteration
```

### Example Evolution Trajectory

```
Iteration 1:  Accuracy: 0.650  (baseline)
Iteration 5:  Accuracy: 0.720  (basic improvements)
Iteration 12: Accuracy: 0.780  (meta agent modifies itself!)
Iteration 25: Accuracy: 0.835  (sophisticated strategies emerge)
Iteration 50: Accuracy: 0.870  (near-optimal performance)
```

---

## Key Files and Their Purpose

```
tachyon_tongs/experiments/darwin_godel_machine/
│
├── src/
│   ├── hyperagent.py           ← The evolving brain
│   ├── archive_manager.py      ← Stores evolutionary history
│   ├── evaluation_engine.py    ← Measures performance
│   └── attack_interface.py     ← Connects to Pathogen
│
├── archive/
│   ├── hyperagents.db          ← SQLite database of all variants
│   └── checkpoints/            ← Saved versions
│       ├── hyperagent_v010.py
│       ├── hyperagent_v025.py
│       └── best_hyperagent.py  ← Top performer
│
├── config/
│   └── dgm_config.yaml         ← Main configuration
│
├── experiments/
│   ├── baseline/               ← Baseline experiment results
│   ├── ablations/              ← Ablation studies
│   └── results/                ← Plots and analysis
│
├── scripts/
│   ├── run_dgm.py              ← Main entry point
│   ├── visualize_evolution.py  ← Generate plots
│   └── analyze_metacognitive_mods.py  ← Study self-modifications
│
└── tests/
    ├── test_hyperagent.py
    └── integration/
```

---

## Integration with Tachyon Tongs

### Using Pathogen for Attack Generation

```python
# attack_interface.py already implements this
from agents.pathogen.agent import PathogenPlugin

pathogen = PathogenPlugin(agent_id="dgm-pathogen", config={...})

# Generate synthetic attacks
attacks = pathogen.execute_action(
    action="generate_variant",
    parameters={
        'asi_type': 'ASI01',  # Goal Hijacking
        'mutation_type': 'homoglyph'
    }
)
```

### Using Sentinel for Verification

```python
# detection_interface.py implements this
from agents.sentinel.agent import SentinelPlugin

sentinel = SentinelPlugin(agent_id="dgm-sentinel", config={...})

# Verify detection accuracy
ground_truth = sentinel.execute_action(
    action="analyze_threat",
    parameters={'prompt': prompt}
)
```

### Herald Notifications

```python
# Herald sends you updates via Signal
from agents.herald.agent import HeraldPlugin

herald.execute_action(
    action="send_alert",
    parameters={
        'title': 'DGM Iteration 50 Complete',
        'message': f'Best accuracy: 0.870',
        'priority': 'INFO'
    }
)
```

---

## Monitoring Progress

### Real-Time Visualization

```bash
# Terminal 1: Run DGM
python scripts/run_dgm.py --iterations 100

# Terminal 2: Watch progress
watch -n 30 'python scripts/visualize_evolution.py'

# Terminal 3: Monitor Herald alerts
tail -f ~/Library/Logs/tachyon_tongs/herald.log
```

### Understanding the Plots

**Plot 1: Evolution Trajectory**
- X-axis: Hyperagent version (generation)
- Y-axis: Detection accuracy
- Blue dots: All variants
- Red line: Running maximum (best so far)

**Plot 2: Metacognitive Modifications**
- Vertical lines: When meta agent modified itself
- Often correlates with performance jumps

**Plot 3: Lineage Tree**
- Parent-child relationships
- Color = accuracy (darker = better)
- Reveals successful lineages

---

## Troubleshooting

### Issue: "No module named 'anthropic'"

```bash
pip install anthropic>=0.18.0
```

### Issue: "ANTHROPIC_API_KEY not found"

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Issue: "Import error: agents.pathogen"

```bash
# Add Tachyon Tongs to Python path
export PYTHONPATH="/path/to/tachyon_tongs:$PYTHONPATH"

# Or add in your script:
import sys
sys.path.append('/path/to/tachyon_tongs')
```

### Issue: Generated hyperagent doesn't compile

- Check logs for syntax errors
- The meta agent includes fallback to return original code
- Increase `max_tokens` in config if code is truncated

### Issue: No improvement after 20 iterations

- Check if test set is too easy/hard
- Review meta agent prompt - it may need tuning
- Inspect individual hyperagent variants for patterns
- Consider running ablation to test if metacognition is working

---

## What to Expect

### First 10 Iterations
- **Goal**: Test the pipeline
- **Expected**: Accuracy improves from ~0.65 to ~0.75
- **Observations**: Basic improvements like better prompts, error handling

### Iterations 10-30
- **Goal**: See metacognitive modifications
- **Expected**: Meta agent starts modifying itself
- **Observations**: New detection strategies, multi-stage pipelines

### Iterations 30-50
- **Goal**: Approach plateau
- **Expected**: Accuracy reaches ~0.85-0.90
- **Observations**: Sophisticated strategies, emergent patterns

### Iterations 50-100
- **Goal**: Refinement and exploration
- **Expected**: Marginal improvements, high diversity
- **Observations**: Code becomes complex, metacognitive modifications stabilize

---

## Next Steps After Initial Run

1. **Analyze Results**
   ```bash
   python scripts/analyze_metacognitive_mods.py
   python scripts/generate_report.py --experiment baseline
   ```

2. **Run Ablations**
   - No metacognition: Test fixed meta agent
   - No archive: Test greedy selection
   - Compare to human-designed baseline

3. **Test Transfer**
   ```bash
   python scripts/evaluate_on_test_set.py \
       --hyperagent archive/checkpoints/best_hyperagent.py \
       --asi-types ASI07,ASI08,ASI09,ASI10,ASI11
   ```

4. **Deploy Best Hyperagent**
   ```bash
   python scripts/export_best_hyperagent.py \
       --output ../../agents/dgm_defense/agent.py
   ```

5. **Continuous Evolution**
   ```bash
   # Set up nightly evolution (cron)
   0 2 * * * cd /path/to/dgm && python scripts/run_dgm.py --iterations 10 --resume
   ```

---

## Research Questions to Explore

1. **How does the meta agent improve itself?**
   - Track modifications to `propose_self_modification()`
   - Measure impact on performance

2. **What defensive strategies emerge?**
   - Analyze evolved hyperagent code
   - Look for novel patterns not in initial seed

3. **How well does it generalize?**
   - Train on ASI01-06, test on ASI07-11
   - Measure zero-shot vs. few-shot performance

4. **How does the archive grow?**
   - Branching factor, lineage depth
   - Diversity metrics

5. **Can it avoid overfitting?**
   - Validation set performance
   - Transfer to new attack types

---

## Common Patterns in Evolved Hyperagents

### Pattern 1: Multi-Stage Detection

```python
def detect_attack(self, prompt, context):
    # Stage 1: Fast pattern matching
    if self._quick_heuristic(prompt):
        # Stage 2: Signature database
        if self._check_signatures(prompt):
            return {'is_attack': True, ...}
    
    # Stage 3: Deep LLM analysis
    return self._llm_detect(prompt, context)
```

### Pattern 2: Persistent Memory

```python
def __init__(self, ...):
    self.attack_patterns = []  # Learned patterns
    
def detect_attack(self, prompt, context):
    # Check learned patterns first
    for pattern in self.attack_patterns:
        if matches(prompt, pattern):
            return {'is_attack': True, ...}
    
    # Learn from new detections
    if result['is_attack']:
        self.attack_patterns.append(extract_pattern(prompt))
```

### Pattern 3: Confidence Calibration

```python
def detect_attack(self, prompt, context):
    result = self._detect(prompt, context)
    
    # Calibrate confidence based on historical accuracy
    calibrated_confidence = self._calibrate(
        result['confidence'],
        self.historical_accuracy_by_type[result['attack_type']]
    )
    
    result['confidence'] = calibrated_confidence
    return result
```

---

## Tips for Success

### 1. Start Small
- Don't run 100 iterations on your first try
- Start with 5-10 to validate the pipeline
- Scale up once you understand the system

### 2. Monitor Closely
- Watch the first 10 iterations in real-time
- Check that hyperagents are actually improving
- Inspect generated code manually

### 3. Save Checkpoints
- Every 10 iterations, save the best hyperagent
- You can always resume from a checkpoint
- Protects against catastrophic forgetting

### 4. Track Metacognition
- Pay special attention when meta agent modifies itself
- These are the most interesting moments
- Often correlate with performance jumps

### 5. Experiment Iteratively
- Run baseline first
- Then try ablations one at a time
- Compare results scientifically

---

## Community and Support

### Share Your Results
- Document emergent strategies you discover
- Contribute improvements to the lab
- Share hyperagent variants that work well

### Get Help
- Check logs first: `tail -f logs/dgm_run.log`
- Review troubleshooting section above
- Inspect failed hyperagents in archive

### Contribute
- Found a bug? Fix it and document
- Discovered a better evaluation metric? Add it
- New meta agent prompt? Test and share

---

## What Makes This Special

Traditional ML: **Fixed architecture, learn parameters**
- Neural network structure is designed by humans
- Training adjusts weights within that structure

AutoML: **Search architectures, learn parameters**
- Automated architecture search (NAS)
- Still constrained by search space

ADAS: **Generate agents, fixed meta agent**
- Meta agent programs new agents
- But meta agent itself is handcrafted

**Darwin-Gödel Machine: Generate agents, evolving meta agent**
- Meta agent programs new agents
- Meta agent can reprogram ITSELF
- True metacognitive self-improvement
- Open-ended evolution

---

## Final Words

You're about to watch an AI system improve not just **what it knows**, but **how it learns**. The Darwin-Gödel Machine is security research meets artificial life.

This isn't just another ML experiment. This is:
- **Evolutionary biology** (archive, selection, mutation)
- **Metacognition** (improving how you improve)
- **Open-ended discovery** (no predetermined strategies)
- **Emergent intelligence** (novel solutions you didn't program)

Start with the baseline experiment. Watch the numbers improve. Then dig into the code to see **what emerged**.

The hyperagent will surprise you.

---

## Quick Command Reference

```bash
# Setup
pip install -r requirements.txt
export ANTHROPIC_API_KEY="..."

# Test
python src/hyperagent.py
python scripts/run_dgm.py --iterations 1

# Run
python scripts/run_dgm.py --iterations 50

# Analyze
python scripts/visualize_evolution.py
python scripts/analyze_metacognitive_mods.py
python scripts/export_best_hyperagent.py

# Deploy
cp archive/checkpoints/best_hyperagent.py ../../agents/dgm_defense/agent.py
```

---

## Document Checklist

Use this to track your implementation:

- [ ] Read darwin_godel_machine_design.md (understand architecture)
- [ ] Read implementation_guide.md Phases 1-2 (setup + core components)
- [ ] Copy hyperagent_template.md code to src/hyperagent.py
- [ ] Test initial hyperagent: `python src/hyperagent.py`
- [ ] Implement archive_manager.py
- [ ] Implement evaluation_engine.py
- [ ] Implement attack_interface.py
- [ ] Implement run_dgm.py
- [ ] Run smoke test: `python scripts/run_dgm.py --iterations 1`
- [ ] Run baseline: `python scripts/run_dgm.py --iterations 50`
- [ ] Visualize results: `python scripts/visualize_evolution.py`
- [ ] Read evaluation_metrics.md (understand measurements)
- [ ] Read experiments_guide.md (run ablations)
- [ ] Deploy best hyperagent to production
- [ ] Set up continuous evolution (optional)

---

## Success Metrics

**You'll know it's working when:**
1. ✓ Accuracy improves over iterations
2. ✓ Meta agent modifies itself (check logs)
3. ✓ Archive shows diverse lineages
4. ✓ Best hyperagent outperforms initial seed by >20%
5. ✓ Transfers to held-out attack types

**You've succeeded when:**
- Accuracy > 0.85 on training set
- TPR > 0.90 (catch 90% of attacks)
- FPR < 0.10 (acceptable false alarms)
- Zero-shot accuracy > 0.75 on new ASI types

---

**Now go forth and evolve!** 🧬🔒

The future of agentic security is self-improving. Let's build it together.
