import os
import argparse
import json
import sys
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from archive_manager import ArchiveManager
from evaluation_engine import EvaluationEngine
from attack_interface import AttackInterface
from detection_interface import DetectionInterface

def run_iteration(args, archive, evaluator, attacker, verifier):
    """Run a single DGM evolution iteration."""
    
    # 1. Selection: Get the current best or latest variant
    parent = archive.get_best_variant() or archive.get_latest_variant()
    
    if parent:
        print(f"[*] Selecting parent version: {parent['version']} (Accuracy: {parent['accuracy']:.3f})")
        parent_code = parent['code']
        parent_version = parent['version']
    else:
        # Load seed from file
        print("[*] No archive found. Loading initial seed from src/hyperagent.py")
        with open(os.path.join(os.path.dirname(__file__), "../src/hyperagent.py"), 'r') as f:
            parent_code = f.read()
        parent_version = None

    # 2. Evaluation: Generate fresh test set
    print(f"[*] Generating test set ({args.num_attacks} attacks, {args.num_benign} benign)...")
    test_set = attacker.generate_test_set(args.num_attacks, args.num_benign)
    
    # 3. Baseline: Evaluate current parent
    print("[*] Evaluating parent...")
    metrics = evaluator.evaluate_variant(parent_code, test_set)
    print(f"[*] Parent Metrics: Accuracy: {metrics['accuracy']:.3f}, F1: {metrics['f1_score']:.3f}")
    
    # If this is the very first run, add the seed to the archive
    if parent_version is None:
        v = archive.add_variant(parent_code, metrics['accuracy'], metrics, modification_notes="Initial Seed")
        parent_version = v
        print(f"[+] Added seed variant as version {v}")

    # 4. Self-Modification: Propose next version
    print("[*] Proposing self-modification...")
    # Instantiate parent class to call its meta agent
    # (Evaluator logic can be reused to load the module)
    tmp_file = "/tmp/dgm_parent_logic.py"
    with open(tmp_file, 'w') as f: f.write(parent_code)
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("parent_logic", tmp_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    parent_agent = module.DefenseHyperagent("parent", archive.config.get('hyperagent_config', {}))
    
    summary = archive.get_recent_summary()
    new_code = parent_agent.propose_self_modification(summary, metrics)
    os.remove(tmp_file)

    # 5. Human-in-the-loop: Review and Approve
    if args.manual_review:
        print("\n" + "="*60)
        print("PROPOSED HYPERAGENT MODIFICATION")
        print("="*60)
        # Show a snippet or diff (simplified for console)
        print(f"New code length: {len(new_code)} chars (vs {len(parent_code)})")
        print("\nFirst 500 characters of new code:")
        print("-" * 20)
        print(new_code[:500])
        print("-" * 20)
        
        confirm = input("\nApply this modification? (y/n): ")
        if confirm.lower() != 'y':
            print("[!] Modification rejected by user.")
            return

    # 6. Finalize: Evaluate child and add to archive
    print("[*] Evaluating child variant...")
    child_metrics = evaluator.evaluate_variant(new_code, test_set)
    print(f"[*] Child Metrics: Accuracy: {child_metrics['accuracy']:.3f}, F1: {child_metrics['f1_score']:.3f}")
    
    improvement = child_metrics['accuracy'] - metrics['accuracy']
    print(f"[*] Improvement: {improvement:+.3f}")
    
    # Use Herald or simple logger to notify
    note = f"Evolved from {parent_version}. Improvement: {improvement:+.3f}"
    v = archive.add_variant(new_code, child_metrics['accuracy'], child_metrics, parent_version, note)
    print(f"[+] Added new version {v} to archive.")
    
    # Save to history for diffs
    from datetime import datetime
    hist_file = os.path.join(os.path.dirname(__file__), f"../src/history/hyperagent_v{v}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
    with open(hist_file, 'w') as f:
        f.write(new_code)
    print(f"[+] Saved version {v} to history for diffing.")
    
    # Update local hyperagent.py for live work
    if args.update_live:
        with open(os.path.join(os.path.dirname(__file__), "../src/hyperagent.py"), 'w') as f:
            f.write(new_code)
        print("[+] Updated src/hyperagent.py with latest version.")

def main():
    parser = argparse.ArgumentParser(description="Darwin-Godel Machine Orchestrator")
    parser.add_argument("--iterations", type=int, default=1, help="Number of evolutionary iterations")
    parser.add_argument("--num-attacks", type=int, default=10, help="Number of attacks per iteration")
    parser.add_argument("--num-benign", type=int, default=5, help="Number of benign prompts per iteration")
    parser.add_argument("--manual-review", action="store_true", help="Enable human-in-the-loop review")
    parser.add_argument("--update-live", action="store_true", help="Update src/hyperagent.py with latest")
    default_db = os.path.join(os.path.dirname(__file__), "../archive/hyperagents.db")
    parser.add_argument("--db", type=str, default=default_db, help="Path to archive database")
    
    args = parser.parse_args()
    
    # Context initialization
    config = {
        'hyperagent_config': {
            'model_path': '/Users/rds/.cache/huggingface/hub/models--mlx-community--Llama-3.2-3B-Instruct-4bit'
        }
    }
    
    archive = ArchiveManager(args.db, config)
    evaluator = EvaluationEngine(config)
    attacker = AttackInterface(config)
    verifier = DetectionInterface(config)
    
    print(f"[*] DGM Started. Archive: {args.db}")
    
    for i in range(args.iterations):
        print(f"\n--- Iteration {i+1}/{args.iterations} ---")
        run_iteration(args, archive, evaluator, attacker, verifier)
        
    print("\n[*] DGM Run Completed.")

if __name__ == "__main__":
    main()
