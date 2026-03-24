# Darwin-Gödel Machine: Implementation Guide
## Step-by-Step Instructions for Building the Self-Evolving Defense System

---

## Overview

This guide provides concrete implementation steps for building the Darwin-Gödel Machine lab within Tachyon Tongs. Follow these steps sequentially to create a working self-improving defense system.

---

## Phase 1: Project Structure Setup

### Step 1.1: Create Directory Structure

```bash
cd tachyon_tongs
mkdir -p experiments/darwin_godel_machine/{src,archive/{runs,checkpoints},config,experiments/{baseline,ablations,results},tests/{integration},scripts}
cd experiments/darwin_godel_machine
```

### Step 1.2: Initialize Python Package

```bash
# Create __init__.py files
touch src/__init__.py
touch tests/__init__.py

# Create basic setup
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="darwin_godel_machine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.18.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "sqlalchemy>=2.0.0",
    ],
)
EOF
```

### Step 1.3: Create Configuration Files

```bash
# Main DGM configuration
cat > config/dgm_config.yaml << 'EOF'
# Darwin-Gödel Machine Configuration

# Anthropic API settings
api:
  model: "claude-sonnet-4-20250514"
  max_tokens: 8000
  api_key_env: "ANTHROPIC_API_KEY"

# Evolution parameters
evolution:
  num_iterations: 100
  archive_size: 1000
  checkpoint_interval: 10
  
# Parent selection
selection:
  strategy: "performance_weighted"
  diversity_penalty: true
  failed_children_weight: 1.0

# Evaluation
evaluation:
  num_attacks_per_type: 20
  num_benign_prompts: 50
  timeout_seconds: 30
  
# Pathogen integration
pathogen:
  agent_id: "dgm-pathogen"
  mutation_types:
    - "homoglyph"
    - "ascii_smuggled"
    - "semantic_drift"
    - "goal_aliasing"
  asi_types:
    - "ASI01"  # Goal Hijacking
    - "ASI02"  # Tool Misuse
    - "ASI03"  # Identity Abuse
    - "ASI05"  # Code Execution
    - "ASI06"  # Memory Poisoning

# Herald integration
herald:
  notifications_enabled: true
  alert_on_improvement: true
  alert_threshold: 0.05  # 5% improvement

# Safety
safety:
  max_file_size_kb: 500
  sandbox_enabled: true
  require_human_review: false
EOF
```

```bash
# Evaluation configuration
cat > config/evaluation_config.yaml << 'EOF'
# Evaluation Metrics Configuration

metrics:
  primary:
    - accuracy
    - f1_score
    - false_positive_rate
  
  secondary:
    - true_positive_rate
    - precision
    - latency_ms
    - adaptation_speed

# Test sets
test_sets:
  training:
    num_attacks: 100
    num_benign: 50
    asi_types: ["ASI01", "ASI02", "ASI03", "ASI05", "ASI06"]
  
  validation:
    num_attacks: 50
    num_benign: 25
    asi_types: ["ASI01", "ASI02", "ASI03", "ASI05", "ASI06"]
  
  test:
    num_attacks: 100
    num_benign: 50
    asi_types: ["ASI07", "ASI08", "ASI09", "ASI10", "ASI11"]  # Held-out

# Performance targets
targets:
  minimum_accuracy: 0.70
  maximum_fpr: 0.10
  minimum_tpr: 0.85
EOF
```

---

## Phase 2: Core Components Implementation

### Step 2.1: Archive Manager

```python
# src/archive_manager.py

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np

class ArchiveManager:
    """
    Manages the archive of evolved hyperagent variants.
    """
    
    def __init__(self, db_path: str = "archive/hyperagents.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hyperagents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hyperagents (
                version INTEGER PRIMARY KEY,
                parent_version INTEGER,
                code_hash TEXT UNIQUE NOT NULL,
                code TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                accuracy REAL,
                false_positive_rate REAL,
                true_positive_rate REAL,
                precision REAL,
                f1_score REAL,
                latency_ms REAL,
                num_children INTEGER DEFAULT 0,
                num_failed_children INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (parent_version) REFERENCES hyperagents(version)
            )
        """)
        
        # Evaluations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hyperagent_version INTEGER NOT NULL,
                attack_id TEXT,
                attack_type TEXT,
                predicted_class TEXT,
                true_class TEXT,
                confidence REAL,
                latency_ms REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hyperagent_version) REFERENCES hyperagents(version)
            )
        """)
        
        # Modifications table (tracks metacognitive changes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hyperagent_version INTEGER NOT NULL,
                modification_type TEXT,
                description TEXT,
                code_diff TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hyperagent_version) REFERENCES hyperagents(version)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add(
        self,
        code: str,
        version: Optional[int] = None,
        parent_version: Optional[int] = None,
        performance: Dict[str, float] = None,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Add a hyperagent variant to the archive.
        
        Args:
            code: Python source code of the hyperagent
            version: Optional version number (auto-assigned if None)
            parent_version: Version of parent hyperagent
            performance: Dictionary of performance metrics
            metadata: Additional metadata
            
        Returns:
            Version number of the added hyperagent
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Compute code hash
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Check if this exact code already exists
        cursor.execute("SELECT version FROM hyperagents WHERE code_hash = ?", (code_hash,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return existing[0]
        
        # Get next version if not provided
        if version is None:
            cursor.execute("SELECT MAX(version) FROM hyperagents")
            max_version = cursor.fetchone()[0]
            version = 0 if max_version is None else max_version + 1
        
        # Extract metrics
        perf = performance or {}
        accuracy = perf.get('accuracy', 0.0)
        fpr = perf.get('false_positive_rate', 0.0)
        tpr = perf.get('true_positive_rate', 0.0)
        precision = perf.get('precision', 0.0)
        f1 = perf.get('f1_score', 0.0)
        latency = perf.get('latency_ms', 0.0)
        
        # Insert hyperagent
        cursor.execute("""
            INSERT INTO hyperagents 
            (version, parent_version, code_hash, code, accuracy, 
             false_positive_rate, true_positive_rate, precision, 
             f1_score, latency_ms, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version, parent_version, code_hash, code, accuracy,
            fpr, tpr, precision, f1, latency,
            json.dumps(metadata) if metadata else None
        ))
        
        # Update parent's child count
        if parent_version is not None:
            cursor.execute("""
                UPDATE hyperagents 
                SET num_children = num_children + 1 
                WHERE version = ?
            """, (parent_version,))
        
        conn.commit()
        conn.close()
        
        return version
    
    def mark_failed(self, parent_version: int):
        """Mark that a child of this parent failed to compile/run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE hyperagents 
            SET num_failed_children = num_failed_children + 1 
            WHERE version = ?
        """, (parent_version,))
        
        conn.commit()
        conn.close()
    
    def select_parent(self) -> Dict[str, Any]:
        """
        Select a parent hyperagent using performance-weighted sampling.
        
        Selection probability ∝ accuracy / (1 + num_failed_children)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all hyperagents with their scores
        cursor.execute("""
            SELECT version, code, accuracy, num_failed_children, metadata
            FROM hyperagents
            ORDER BY version
        """)
        
        candidates = []
        scores = []
        
        for row in cursor.fetchall():
            version, code, accuracy, failed_children, metadata = row
            
            # Compute selection score
            score = accuracy / (1 + failed_children)
            
            candidates.append({
                'version': version,
                'code': code,
                'accuracy': accuracy,
                'metadata': json.loads(metadata) if metadata else {}
            })
            scores.append(score)
        
        conn.close()
        
        if not candidates:
            raise ValueError("Archive is empty")
        
        # Normalize to probabilities
        total = sum(scores)
        if total == 0:
            probabilities = [1.0 / len(scores)] * len(scores)
        else:
            probabilities = [s / total for s in scores]
        
        # Sample parent
        idx = np.random.choice(len(candidates), p=probabilities)
        
        return candidates[idx]
    
    def get_best_hyperagent(self) -> Dict[str, Any]:
        """Get the hyperagent with the highest accuracy."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version, code, accuracy, metadata
            FROM hyperagents
            ORDER BY accuracy DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ValueError("Archive is empty")
        
        return {
            'version': row[0],
            'code': row[1],
            'accuracy': row[2],
            'metadata': json.loads(row[3]) if row[3] else {}
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the archive."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), MAX(accuracy), AVG(accuracy) FROM hyperagents")
        total, best_acc, avg_acc = cursor.fetchone()
        
        cursor.execute("SELECT version, accuracy FROM hyperagents ORDER BY timestamp DESC LIMIT 10")
        recent = [{'version': v, 'accuracy': a} for v, a in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_variants': total or 0,
            'best_accuracy': best_acc or 0.0,
            'average_accuracy': avg_acc or 0.0,
            'recent_variants': recent
        }
    
    def checkpoint(self, iteration: int):
        """Save a checkpoint of the archive."""
        best = self.get_best_hyperagent()
        
        checkpoint_path = f"archive/checkpoints/hyperagent_v{best['version']:04d}_iter{iteration}.py"
        with open(checkpoint_path, 'w') as f:
            f.write(best['code'])
        
        print(f"Checkpoint saved: {checkpoint_path}")
```

### Step 2.2: Evaluation Engine

```python
# src/evaluation_engine.py

import time
import subprocess
import tempfile
from typing import Dict, Any, List
import numpy as np

class EvaluationEngine:
    """
    Evaluates hyperagent performance on synthetic attacks.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get('timeout_seconds', 30)
    
    def evaluate_hyperagent(
        self,
        hyperagent_code: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate a hyperagent on a set of test cases.
        
        Args:
            hyperagent_code: Python code of the hyperagent
            test_cases: List of test cases with 'prompt' and 'ground_truth'
            
        Returns:
            Dictionary of performance metrics
        """
        # Write hyperagent to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(hyperagent_code)
            hyperagent_path = f.name
        
        results = []
        latencies = []
        
        for test_case in test_cases:
            prompt = test_case['prompt']
            ground_truth = test_case['ground_truth']
            
            # Run detection in subprocess (sandboxed)
            start_time = time.time()
            
            try:
                result = self._run_detection_sandboxed(
                    hyperagent_path,
                    prompt,
                    test_case.get('context', {})
                )
                latency = (time.time() - start_time) * 1000  # ms
                
                prediction = result.get('is_attack', False)
                confidence = result.get('confidence', 0.0)
                
            except Exception as e:
                print(f"Error evaluating on test case: {e}")
                prediction = False
                confidence = 0.0
                latency = self.timeout * 1000
            
            results.append({
                'ground_truth': ground_truth,
                'prediction': prediction,
                'confidence': confidence,
                'correct': (ground_truth == prediction)
            })
            latencies.append(latency)
        
        # Compute metrics
        metrics = self._compute_metrics(results)
        metrics['latency_ms'] = np.mean(latencies)
        
        return metrics
    
    def _run_detection_sandboxed(
        self,
        hyperagent_path: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run detection in a sandboxed subprocess.
        """
        # Create runner script
        runner_code = f"""
import sys
import json
sys.path.insert(0, '{self.config.get("tachyon_root", "../..")}')

# Import hyperagent
import importlib.util
spec = importlib.util.spec_from_file_location("hyperagent", "{hyperagent_path}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Instantiate hyperagent
hyperagent = module.DefenseHyperagent(
    hyperagent_id="eval-instance",
    config={json.dumps(self.config.get('hyperagent_config', {}))}
)

# Run detection
prompt = {json.dumps(prompt)}
context = {json.dumps(context)}
result = hyperagent.detect_attack(prompt, context)

# Output result
print(json.dumps(result))
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(runner_code)
            runner_path = f.name
        
        # Run with timeout
        try:
            output = subprocess.check_output(
                ['python', runner_path],
                timeout=self.timeout,
                stderr=subprocess.PIPE,
                text=True
            )
            result = json.loads(output.strip())
            return result
            
        except subprocess.TimeoutExpired:
            raise Exception("Detection timed out")
        except Exception as e:
            raise Exception(f"Detection failed: {e}")
    
    def _compute_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute performance metrics from results."""
        tp = sum(1 for r in results if r['ground_truth'] and r['prediction'])
        tn = sum(1 for r in results if not r['ground_truth'] and not r['prediction'])
        fp = sum(1 for r in results if not r['ground_truth'] and r['prediction'])
        fn = sum(1 for r in results if r['ground_truth'] and not r['prediction'])
        
        total = tp + tn + fp + fn
        
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
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'true_positives': tp,
            'true_negatives': tn,
            'false_positives': fp,
            'false_negatives': fn
        }
```

### Step 2.3: Attack Generator Interface

```python
# src/attack_interface.py

import sys
sys.path.append('../..')  # Add tachyon_tongs to path

from typing import Dict, Any, List
import numpy as np
from agents.pathogen.agent import PathogenPlugin

class AttackGeneratorInterface:
    """
    Interface to Tachyon Tongs' Pathogen agent for attack generation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize Pathogen agent
        self.pathogen = PathogenPlugin(
            agent_id=config.get('agent_id', 'dgm-pathogen'),
            config=config
        )
        
        # Load ASI catalog
        self.asi_types = config.get('asi_types', [
            'ASI01', 'ASI02', 'ASI03', 'ASI05', 'ASI06'
        ])
        
        self.mutation_types = config.get('mutation_types', [
            'homoglyph', 'ascii_smuggled', 'semantic_drift'
        ])
    
    def generate_test_set(
        self,
        num_attacks: int,
        num_benign: int,
        asi_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a complete test set with attacks and benign prompts.
        
        Returns:
            List of test cases with 'prompt', 'ground_truth', 'type', 'mutation'
        """
        test_cases = []
        
        # Generate attacks
        attacks = self.generate_attacks(
            num_attacks=num_attacks,
            attack_types=asi_types or self.asi_types
        )
        test_cases.extend(attacks)
        
        # Generate benign prompts
        benign = self.generate_benign_prompts(num_prompts=num_benign)
        test_cases.extend(benign)
        
        # Shuffle
        np.random.shuffle(test_cases)
        
        return test_cases
    
    def generate_attacks(
        self,
        num_attacks: int,
        attack_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate synthetic attacks using Pathogen."""
        attacks = []
        
        for _ in range(num_attacks):
            # Select random attack type and mutation
            asi_type = np.random.choice(attack_types)
            mutation = np.random.choice(self.mutation_types)
            
            # Use Pathogen to generate attack
            result = self.pathogen.execute_action(
                action="generate_variant",
                parameters={
                    'asi_type': asi_type,
                    'mutation_type': mutation
                }
            )
            
            attacks.append({
                'prompt': result['payload'],
                'ground_truth': True,
                'type': asi_type,
                'mutation': mutation,
                'context': {
                    'source': 'pathogen',
                    'template_id': result.get('template_id')
                }
            })
        
        return attacks
    
    def generate_benign_prompts(self, num_prompts: int) -> List[Dict[str, Any]]:
        """Generate benign prompts for false positive testing."""
        benign_prompts = []
        
        # TODO: Integrate with Tachyon's benign prompt corpus
        # For now, use simple examples
        benign_templates = [
            "What is the weather today?",
            "Can you help me write a Python function to sort a list?",
            "Explain quantum computing in simple terms.",
            "What are the best practices for API design?",
            "How do I debug a memory leak in my application?",
        ]
        
        for _ in range(num_prompts):
            template = np.random.choice(benign_templates)
            
            benign_prompts.append({
                'prompt': template,
                'ground_truth': False,
                'type': 'benign',
                'mutation': None,
                'context': {
                    'source': 'benign_corpus'
                }
            })
        
        return benign_prompts
```

### Step 2.4: Main DGM Runner

```python
# scripts/run_dgm.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import yaml
import argparse
from archive_manager import ArchiveManager
from evaluation_engine import EvaluationEngine
from attack_interface import AttackGeneratorInterface

def load_initial_hyperagent() -> str:
    """Load the initial hyperagent code."""
    initial_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'src', 
        'hyperagent.py'
    )
    
    with open(initial_path, 'r') as f:
        return f.read()

def instantiate_hyperagent(code: str, config: Dict[str, Any]):
    """Dynamically load hyperagent from code string."""
    import tempfile
    import importlib.util
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    # Import
    spec = importlib.util.spec_from_file_location("hyperagent_module", temp_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Instantiate
    hyperagent = module.DefenseHyperagent(
        hyperagent_id=f"hyperagent-{config['iteration']}",
        config=config['hyperagent_config']
    )
    
    return hyperagent

def run_darwin_godel_machine(config: Dict[str, Any]):
    """Main evolutionary loop."""
    print("=" * 80)
    print("Darwin-Gödel Machine for Tachyon Tongs")
    print("=" * 80)
    print()
    
    # Initialize components
    archive = ArchiveManager(db_path=config['archive']['db_path'])
    evaluator = EvaluationEngine(config['evaluation'])
    attack_gen = AttackGeneratorInterface(config['pathogen'])
    
    # Load initial hyperagent
    print("Loading initial hyperagent...")
    initial_code = load_initial_hyperagent()
    
    # Add to archive
    archive.add(
        code=initial_code,
        version=0,
        parent_version=None,
        performance={'accuracy': 0.0},
        metadata={'description': 'Initial hyperagent'}
    )
    print("Initial hyperagent added to archive (v0)")
    print()
    
    # Main evolution loop
    num_iterations = config['evolution']['num_iterations']
    
    for iteration in range(1, num_iterations + 1):
        print(f"\n{'=' * 80}")
        print(f"Iteration {iteration}/{num_iterations}")
        print('=' * 80)
        
        try:
            # 1. SELECT PARENT
            parent = archive.select_parent()
            print(f"Selected parent: v{parent['version']} (accuracy: {parent['accuracy']:.3f})")
            
            # 2. GENERATE CHILD via metacognitive self-modification
            print("Generating child variant...")
            
            parent_hyperagent = instantiate_hyperagent(
                parent['code'],
                {'iteration': iteration, 'hyperagent_config': config['api']}
            )
            
            child_code = parent_hyperagent.propose_self_modification(
                archive_data=archive.get_summary(),
                evaluation_results=parent.get('last_eval', {})
            )
            
            # 3. EVALUATE CHILD
            print("Evaluating child hyperagent...")
            
            test_cases = attack_gen.generate_test_set(
                num_attacks=config['evaluation']['num_attacks_per_type'] * len(config['pathogen']['asi_types']),
                num_benign=config['evaluation']['num_benign_prompts']
            )
            
            performance = evaluator.evaluate_hyperagent(child_code, test_cases)
            
            print(f"Child performance:")
            print(f"  - Accuracy: {performance['accuracy']:.3f}")
            print(f"  - F1 Score: {performance['f1_score']:.3f}")
            print(f"  - FPR: {performance['false_positive_rate']:.3f}")
            print(f"  - TPR: {performance['true_positive_rate']:.3f}")
            
            # 4. ADD TO ARCHIVE
            child_version = archive.add(
                code=child_code,
                parent_version=parent['version'],
                performance=performance,
                metadata={
                    'iteration': iteration,
                    'test_set_size': len(test_cases)
                }
            )
            
            print(f"Added child to archive (v{child_version})")
            
            # 5. CHECKPOINT
            if iteration % config['evolution']['checkpoint_interval'] == 0:
                archive.checkpoint(iteration)
            
        except Exception as e:
            print(f"ERROR in iteration {iteration}: {e}")
            # Mark parent as having failed child
            if 'parent' in locals():
                archive.mark_failed(parent['version'])
            continue
    
    # Final summary
    print(f"\n{'=' * 80}")
    print("Evolution Complete!")
    print('=' * 80)
    
    best = archive.get_best_hyperagent()
    print(f"Best hyperagent: v{best['version']}")
    print(f"  - Accuracy: {best['accuracy']:.3f}")
    print(f"  - Code saved to: archive/checkpoints/best_hyperagent.py")
    
    # Save best hyperagent
    with open('archive/checkpoints/best_hyperagent.py', 'w') as f:
        f.write(best['code'])

def main():
    parser = argparse.ArgumentParser(description="Run Darwin-Gödel Machine")
    parser.add_argument('--config', default='config/dgm_config.yaml', help='Config file')
    parser.add_argument('--iterations', type=int, help='Override number of iterations')
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override iterations if provided
    if args.iterations:
        config['evolution']['num_iterations'] = args.iterations
    
    # Add archive path
    config['archive'] = {
        'db_path': 'archive/hyperagents.db'
    }
    
    # Run DGM
    run_darwin_godel_machine(config)

if __name__ == '__main__':
    main()
```

---

## Phase 3: Testing and Validation

### Step 3.1: Unit Tests

```python
# tests/test_archive.py

import unittest
import os
import tempfile
from src.archive_manager import ArchiveManager

class TestArchiveManager(unittest.TestCase):
    def setUp(self):
        # Create temp database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.archive = ArchiveManager(db_path=self.temp_db.name)
    
    def tearDown(self):
        os.unlink(self.temp_db.name)
    
    def test_add_hyperagent(self):
        """Test adding a hyperagent to archive."""
        code = "def test(): pass"
        version = self.archive.add(
            code=code,
            version=0,
            performance={'accuracy': 0.75}
        )
        
        self.assertEqual(version, 0)
    
    def test_select_parent(self):
        """Test parent selection."""
        # Add multiple variants
        for i in range(5):
            self.archive.add(
                code=f"def test{i}(): pass",
                version=i,
                performance={'accuracy': 0.5 + i * 0.1}
            )
        
        # Select parent (should work without error)
        parent = self.archive.select_parent()
        self.assertIn('version', parent)
        self.assertIn('code', parent)
    
    def test_get_best(self):
        """Test getting best hyperagent."""
        # Add variants with different accuracies
        self.archive.add(code="v1", version=1, performance={'accuracy': 0.6})
        self.archive.add(code="v2", version=2, performance={'accuracy': 0.9})
        self.archive.add(code="v3", version=3, performance={'accuracy': 0.7})
        
        best = self.archive.get_best_hyperagent()
        self.assertEqual(best['version'], 2)
        self.assertEqual(best['accuracy'], 0.9)

if __name__ == '__main__':
    unittest.main()
```

### Step 3.2: Integration Test

```python
# tests/integration/test_full_pipeline.py

import unittest
import yaml
from src.archive_manager import ArchiveManager
from src.evaluation_engine import EvaluationEngine
from src.attack_interface import AttackGeneratorInterface

class TestFullPipeline(unittest.TestCase):
    def setUp(self):
        # Load test config
        with open('config/dgm_config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
    
    def test_end_to_end(self):
        """Test one complete iteration of the DGM."""
        # This is a smoke test to ensure all components work together
        
        # Initialize components
        archive = ArchiveManager(db_path=':memory:')
        attack_gen = AttackGeneratorInterface(self.config['pathogen'])
        
        # Add initial hyperagent
        initial_code = "# Test hyperagent\\nclass DefenseHyperagent:\\n    pass"
        archive.add(code=initial_code, version=0, performance={'accuracy': 0.5})
        
        # Generate test cases
        test_cases = attack_gen.generate_test_set(
            num_attacks=10,
            num_benign=5
        )
        
        self.assertEqual(len(test_cases), 15)
        self.assertTrue(any(t['ground_truth'] for t in test_cases))
        self.assertTrue(any(not t['ground_truth'] for t in test_cases))

if __name__ == '__main__':
    unittest.main()
```

---

## Phase 4: Running Experiments

### Step 4.1: Baseline Run

```bash
# Run with minimal iterations to test
python scripts/run_dgm.py --iterations 5

# Full run
python scripts/run_dgm.py --config config/dgm_config.yaml
```

### Step 4.2: Monitor Progress

```python
# scripts/visualize_evolution.py

import sqlite3
import matplotlib.pyplot as plt
import argparse

def visualize_evolution(db_path: str):
    """Create plots showing evolutionary progress."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all hyperagents over time
    cursor.execute("""
        SELECT version, accuracy, timestamp
        FROM hyperagents
        ORDER BY version
    """)
    
    data = cursor.fetchall()
    versions = [d[0] for d in data]
    accuracies = [d[1] for d in data]
    
    # Plot accuracy over generations
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(versions, accuracies, 'b-', alpha=0.3)
    plt.scatter(versions, accuracies, c=accuracies, cmap='viridis')
    plt.xlabel('Hyperagent Version')
    plt.ylabel('Accuracy')
    plt.title('Evolution of Detection Accuracy')
    plt.grid(True)
    plt.colorbar(label='Accuracy')
    
    # Plot running maximum
    plt.subplot(1, 2, 2)
    max_acc = []
    current_max = 0
    for acc in accuracies:
        current_max = max(current_max, acc)
        max_acc.append(current_max)
    
    plt.plot(versions, max_acc, 'r-', linewidth=2)
    plt.xlabel('Hyperagent Version')
    plt.ylabel('Best Accuracy So Far')
    plt.title('Cumulative Best Performance')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('experiments/results/evolution_progress.png', dpi=300)
    print("Saved plot: experiments/results/evolution_progress.png")
    
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='archive/hyperagents.db')
    args = parser.parse_args()
    
    visualize_evolution(args.db)
```

---

## Phase 5: Analysis and Iteration

### Step 5.1: Export Best Hyperagent

```bash
# scripts/export_best_hyperagent.py

import sqlite3
import argparse

def export_best(db_path: str, output_path: str):
    """Export the best hyperagent for production use."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT version, code, accuracy
        FROM hyperagents
        ORDER BY accuracy DESC
        LIMIT 1
    """)
    
    version, code, accuracy = cursor.fetchone()
    
    with open(output_path, 'w') as f:
        f.write(f"# Best Hyperagent - Version {version}\\n")
        f.write(f"# Accuracy: {accuracy:.3f}\\n")
        f.write(f"#\\n")
        f.write(code)
    
    print(f"Exported best hyperagent (v{version}, accuracy={accuracy:.3f})")
    print(f"Saved to: {output_path}")
    
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='archive/hyperagents.db')
    parser.add_argument('--output', default='../../agents/dgm_defense/agent.py')
    args = parser.parse_args()
    
    export_best(args.db, args.output)
```

### Step 5.2: Analyze Metacognitive Modifications

```python
# scripts/analyze_metacognitive_mods.py

import sqlite3
import difflib
import argparse

def analyze_modifications(db_path: str):
    """Analyze how the meta agent evolved itself."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all hyperagents in order
    cursor.execute("""
        SELECT version, code, parent_version
        FROM hyperagents
        ORDER BY version
    """)
    
    variants = cursor.fetchall()
    
    print("Metacognitive Modification Analysis")
    print("=" * 80)
    
    for version, code, parent_version in variants:
        if parent_version is None:
            continue
        
        # Get parent code
        cursor.execute("SELECT code FROM hyperagents WHERE version = ?", (parent_version,))
        parent_code = cursor.fetchone()[0]
        
        # Compute diff
        diff = difflib.unified_diff(
            parent_code.splitlines(),
            code.splitlines(),
            lineterm='',
            fromfile=f'v{parent_version}',
            tofile=f'v{version}'
        )
        
        diff_lines = list(diff)
        
        # Check if meta agent was modified
        meta_agent_modified = any(
            'propose_self_modification' in line
            for line in diff_lines
        )
        
        if meta_agent_modified:
            print(f"\\nVersion {version}: META AGENT MODIFIED")
            print("-" * 80)
            for line in diff_lines[:50]:  # Show first 50 lines
                print(line)
            print("...")
    
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='archive/hyperagents.db')
    args = parser.parse_args()
    
    analyze_modifications(args.db)
```

---

## Phase 6: Integration with Tachyon Tongs

### Step 6.1: Deploy as Agent

Once you have a high-performing hyperagent:

```bash
# 1. Export best hyperagent
python scripts/export_best_hyperagent.py --output ../../agents/dgm_defense/agent.py

# 2. Create agent config
cat > ../../agents/dgm_defense/config.yaml << 'EOF'
agent_id: "dgm-defense-001"
name: "DGM Defense"
description: "Evolved defense agent from Darwin-Gödel Machine"
type: "hybrid"
entry_point: "agents.dgm_defense.agent:DGMDefensePlugin"
EOF

# 3. Register with agent registry
python -c "
from agents._core.registry import AgentRegistry
registry = AgentRegistry()
registry.discover_plugins('agents')
print(f'Registered: {registry.list_plugins()}')
"
```

### Step 6.2: Continuous Evolution

Set up a cron job for continuous evolution:

```bash
# Add to crontab
0 2 * * * cd /path/to/tachyon_tongs/experiments/darwin_godel_machine && python scripts/run_dgm.py --iterations 10
```

---

## Troubleshooting

### Common Issues

**Issue 1: Import errors**
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=/path/to/tachyon_tongs:$PYTHONPATH
```

**Issue 2: Hyperagent fails to compile**
- Check syntax errors in generated code
- Add validation step in meta agent
- Increase timeout for LLM calls

**Issue 3: No improvement in accuracy**
- Check if test set is too easy/hard
- Increase number of iterations
- Adjust parent selection strategy
- Review meta agent prompts

**Issue 4: Memory errors**
- Reduce archive size
- Add cleanup of old checkpoints
- Use streaming evaluation

---

## Next Steps

1. **Run baseline experiment**: 50-100 iterations
2. **Analyze results**: Use visualization scripts
3. **Tune hyperparameters**: Parent selection, mutation rate
4. **Ablation studies**: Test without metacognitive modification
5. **Transfer learning**: Test on held-out ASI types
6. **Production deployment**: Integrate best agent into Tachyon Tongs

---

## Conclusion

You now have a complete implementation guide for the Darwin-Gödel Machine. The system will autonomously evolve better defense mechanisms through metacognitive self-modification, leveraging Tachyon Tongs' existing infrastructure for attack generation (Pathogen) and verification (Sentinel/Guardian).

Start with a small-scale experiment (5-10 iterations) to validate the pipeline, then scale up to longer runs (100+ iterations) to observe emergent defensive strategies.

Happy evolving! 🧬
