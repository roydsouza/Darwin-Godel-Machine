#!/usr/bin/env python3
import os
import argparse
import json
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from archive_manager import ArchiveManager
from evaluation_engine import EvaluationEngine
from attack_interface import AttackInterface
from detection_interface import DetectionInterface
from hyperagent import DefenseHyperagent

def run_iteration(args, archive, evaluator, attacker, verifier):
    """Run a single DGM evolution iteration for the modular brain."""
    
    # 1. Selection: Get the current best brain version
    parent = archive.get_best_variant() or archive.get_latest_variant()
    
    if parent:
        print(f"[*] Selecting parent brain version: {parent['version']} (Accuracy: {parent['accuracy']:.3f})")
        parent_brain_code = parent['code']
        parent_version = parent['version']
    else:
        # Load seed brain from file
        brain_path = os.path.join(os.path.dirname(__file__), "../src/logic/brain.py")
        print(f"[*] No archive found. Loading initial seed brain from {brain_path}")
        with open(brain_path, 'r') as f:
            parent_brain_code = f.read()
        parent_version = None

    # 2. Evaluation: Generate fresh test set
    print(f"[*] Generating test set ({args.num_attacks} attacks, {args.num_benign} benign)...")
    test_set = attacker.generate_test_set(args.num_attacks, args.num_benign)
    
    # 3. Baseline: Evaluate current parent brain
    # We must temporarily write the parent_brain_code to logic/brain.py so the Hyperagent can use it
    brain_path = os.path.join(os.path.dirname(__file__), "../src/logic/brain.py")
    with open(brain_path, 'w') as f:
        f.write(parent_brain_code)
        
    print("[*] Evaluating parent brain...")
    # The evaluator uses the Hyperagent runner which loads the brain
    # We need to make sure the evaluator loads the latest brain from disk
    # (Actually EvaluationEngine.evaluate_variant handles writing code to a temp file, 
    # but it expects hyperagent code, not brain code. Let's fix that in next iteration or 
    # just create a full hyperagent mock here).
    
    # For now, let's just use a simple evaluation call
    agent = DefenseHyperagent("evaluator", archive.config.get('hyperagent_config', {}))
    metrics = evaluator.evaluate_variant(None, test_set) # Passing None because it's already on disk
    
    # Check if metrics contains f1_score
    if 'f1_score' not in metrics: metrics['f1_score'] = 0.0
    
    print(f"[*] Parent Metrics: Accuracy: {metrics['accuracy']:.3f}, F1: {metrics['f1_score']:.3f}")
    
    if parent_version is None:
        v = archive.add_variant(parent_brain_code, metrics['accuracy'], metrics, modification_notes="Initial Seed Brain")
        parent_version = v
        print(f"[+] Added seed brain as version {v}")

    # 4. Self-Modification: Propose next version
    print("[*] Proposing brain self-modification...")
    summary = archive.get_recent_summary()
    new_brain_code = agent.propose_self_modification(summary, metrics)

    # 5. Human-in-the-loop: Review and Approve
    if args.manual_review:
        print("\n" + "="*60)
        print("PROPOSED MODULAR BRAIN MODIFICATION")
        print("="*60)
        print(f"New brain length: {len(new_brain_code)} chars (vs {len(parent_brain_code)})")
        print("\nFirst 500 characters of new brain code:")
        print("-" * 20)
        print(new_brain_code[:500])
        print("-" * 20)
        
        confirm = input("\nApply this modification? (y/n): ")
        if confirm.lower() != 'y':
            print("[!] Modification rejected by user.")
            return

    # 6. Finalize: Evaluate child and add to archive
    # Write child to disk for evaluation
    with open(brain_path, 'w') as f:
        f.write(new_brain_code)
    
    print("[*] Evaluating child brain...")
    child_metrics = evaluator.evaluate_variant(None, test_set)
    if 'f1_score' not in child_metrics: child_metrics['f1_score'] = 0.0
    
    print(f"[*] Child Metrics: Accuracy: {child_metrics['accuracy']:.3f}, F1: {child_metrics['f1_score']:.3f}")
    
    improvement = child_metrics['accuracy'] - metrics['accuracy']
    print(f"[*] Improvement: {improvement:+.3f}")
    
    note = f"Evolved brain from {parent_version}. Improvement: {improvement:+.3f}"
    v = archive.add_variant(new_brain_code, child_metrics['accuracy'], child_metrics, parent_version, note)
    print(f"[+] Added new brain version {v} to archive.")
    
    # Update local brain.py for live work
    if args.update_live:
        print("[+] Brain logic updated in src/logic/brain.py.")
    else:
        # Revert to parent if not updating live
        with open(brain_path, 'w') as f:
            f.write(parent_brain_code)

    # Print Iteration Summary
    print("\n" + "="*30)
    print(f" ITERATION {parent_version if parent_version is not None else 0} -> {v} SUMMARY")
    print("="*30)
    print(f" Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f" Parent Acc: {metrics['accuracy']:.3f}")
    print(f" Child Acc:  {child_metrics['accuracy']:.3f} ({improvement:+.3f})")
    print(f" Status:     {'IMPROVED' if improvement > 0 else 'STAGNANT'}")
    print("="*30 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Darwin-Godel Machine Orchestrator (Modular)")
    parser.add_argument("--iterations", type=int, default=1, help="Number of evolutionary iterations")
    parser.add_argument("--num-attacks", type=int, default=10, help="Number of attacks per iteration")
    parser.add_argument("--num-benign", type=int, default=5, help="Number of benign prompts per iteration")
    parser.add_argument("--manual-review", action="store_true", help="Enable human-in-the-loop review")
    parser.add_argument("--update-live", action="store_true", help="Update src/logic/brain.py with latest")
    default_db = os.path.join(os.path.dirname(__file__), "../archive/hyperagents.db")
    parser.add_argument("--db", type=str, default=default_db, help="Path to archive database")
    
    args = parser.parse_args()
    
    config = {
        'hyperagent_config': {
            'model_path': 'mlx-community/Llama-3.2-3B-Instruct-4bit'
        }
    }
    
    archive = ArchiveManager(args.db, config)
    evaluator = EvaluationEngine(config)
    attacker = AttackInterface(config)
    verifier = DetectionInterface(config)
    
    print(f"[*] DGM Started (Modular). Archive: {args.db}")
    
    for i in range(args.iterations):
        print(f"\n--- Iteration {i+1}/{args.iterations} ---")
        run_iteration(args, archive, evaluator, attacker, verifier)
        
    print("\n[*] DGM Run Completed.")

if __name__ == "__main__":
    main()
