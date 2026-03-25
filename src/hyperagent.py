"""
Darwin-Gödel Machine Hyperagent (Modular MLX Native)
====================================================

Runner agent that manages the mutable Task Brain.
"""

import json
import os
import sys
from typing import Dict, Any, List
from mlx_lm import load, generate

import logic.brain as brain

class DefenseHyperagent:
    def __init__(self, hyperagent_id: str, config: Dict[str, Any]):
        self.hyperagent_id = hyperagent_id
        self.config = config
        self.model_path = config.get('model_path', 'mlx-community/Llama-3.2-3B-Instruct-4bit')
        self.model = None
        self.tokenizer = None
        
    def _ensure_model(self):
        if self.model is None:
            self.model, self.tokenizer = load(self.model_path)

    def _model_runner(self, prompt: str, max_tokens: int = 1000) -> str:
        self._ensure_model()
        return generate(self.model, self.tokenizer, prompt=prompt, verbose=False, max_tokens=max_tokens)

    # ============================================================
    # TASK AGENT: Outsourced to logic/brain.py
    # ============================================================
    
    def detect_attack(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return brain.detect_attack(prompt, context, self._model_runner)

    # ============================================================
    # META AGENT: Evolves logic/brain.py
    # ============================================================
    
    def propose_self_modification(self, archive_data: Dict[str, Any], evaluation_results: Dict[str, Any]) -> str:
        self._ensure_model()
        brain_path = os.path.join(os.path.dirname(__file__), "logic/brain.py")
        with open(brain_path, 'r') as f:
            current_brain_code = f.read()
        
        meta_prompt = f"""You are a Meta-Evolutionary Agent for the Darwin-Godel Machine.
Improve the following BRAIN LOGIC to increase detection accuracy.

EVALUATION RESULTS:
{json.dumps(evaluation_results, indent=2)}

CURRENT BRAIN CODE:
{current_brain_code}

INSTRUCTIONS:
1. Return ONLY the COMPLETE Python code for the brain module.
2. The code MUST contain the 'detect_attack' function.
3. Keep the signature: detect_attack(prompt, context, model_runner).
4. NO markdown. NO preamble.
"""

        formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a security code generator. Respond ONLY with Python code.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{meta_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

        try:
            new_brain_code = self._model_runner(formatted_prompt, max_tokens=4000)
            
            # Cleanup
            new_brain_code = new_brain_code.strip()
            if "def detect_attack" not in new_brain_code:
                print("[!] Meta-agent failed: Function not found. Reverting.")
                return current_brain_code

            if "```" in new_brain_code:
                lines = new_brain_code.split('\n')
                if lines[0].startswith("```"): lines = lines[1:]
                if lines[-1].startswith("```"): lines = lines[:-1]
                new_brain_code = '\n'.join(lines)
            
            return new_brain_code
        except Exception as e:
            print(f"Meta agent failed: {e}")
            return current_brain_code

if __name__ == '__main__':
    agent = DefenseHyperagent("seed-v0", {'model_path': 'mlx-community/Llama-3.2-3B-Instruct-4bit'})
    print("Modular Hyperagent (MLX) initialized.")
