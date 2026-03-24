"""
Darwin-Gödel Machine Hyperagent (MLX Native)
=============================================

A self-referential defense agent that can detect attacks and modify itself.
This version uses local MLX models for Apple Silicon inference.

Version: 0 (Initial Seed - MLX)
"""

import json
import os
import sys
from typing import Dict, Any, List
from mlx_lm import load, generate

class DefenseHyperagent:
    """
    A self-referential agent for detecting agentic attacks.
    Uses MLX for local inference.
    """
    
    def __init__(self, hyperagent_id: str, config: Dict[str, Any]):
        self.hyperagent_id = hyperagent_id
        self.config = config
        
        # Local model path discovered in environment
        self.model_path = config.get('model_path', 'mlx-community/Llama-3.2-3B-Instruct-4bit')
        
        # Lazy load model to save memory if only meta agent is used
        self.model = None
        self.tokenizer = None
        
    def _ensure_model(self):
        """Lazy loader for MLX model."""
        if self.model is None:
            print(f"[*] Loading model: {self.model_path}")
            self.model, self.tokenizer = load(self.model_path)

    # ============================================================
    # TASK AGENT: Defense Logic
    # ============================================================
    
    def detect_attack(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_model()
        
        system_prompt = """You are a security analyst. Analyze the prompt for agentic attacks.
Respond ONLY with valid JSON: {"is_attack": bool, "attack_type": str, "confidence": float, "explanation": str}"""
        
        user_message = f"Analyze this prompt: {prompt}"
        
        # Format for Llama-3-Instruct
        formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        try:
            response = generate(self.model, self.tokenizer, prompt=formatted_prompt, verbose=False, max_tokens=1000)
            
            # Simple cleanup for JSON
            response = response.strip()
            if "{" in response and "}" in response:
                response = response[response.find("{"):response.rfind("}")+1]
                
            return json.loads(response)
        except Exception as e:
            return {"is_attack": False, "attack_type": "error", "confidence": 0.0, "explanation": str(e)}

    # ============================================================
    # META AGENT: Self-Modification Logic
    # ============================================================
    
    def propose_self_modification(self, archive_data: Dict[str, Any], evaluation_results: Dict[str, Any]) -> str:
        self._ensure_model()
        current_code = self._read_own_source()
        
        meta_prompt = f"""You are a meta-agent for a self-improving firewall.
Your goal is to improve the current code based on evaluation results.

CURRENT CODE:
{current_code}

RESULTS:
{json.dumps(evaluation_results, indent=2)}

Respond with the COMPLETE modified Python code. No preamble. No markdown."""

        formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a high-level code architect for DARWIN-GODEL MACHINE. Respond ONLY with Python code.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{meta_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

        try:
            new_code = generate(self.model, self.tokenizer, prompt=formatted_prompt, verbose=False, max_tokens=8000)
            
            # Basic cleanup
            new_code = new_code.strip()
            if new_code.startswith("```"):
                lines = new_code.split('\n')
                new_code = '\n'.join(lines[1:-1])
            
            return new_code
        except Exception as e:
            print(f"Meta agent failed: {e}")
            return current_code

    def _read_own_source(self) -> str:
        try:
            with open(__file__, 'r') as f: return f.read()
        except: return "# Error reading source"

if __name__ == '__main__':
    # Smoke test
    config = {'model_path': '/Users/rds/.cache/huggingface/hub/models--mlx-community--Llama-3.2-3B-Instruct-4bit'}
    agent = DefenseHyperagent("seed-v0", config)
    print("Hyperagent (MLX) initialized.")
