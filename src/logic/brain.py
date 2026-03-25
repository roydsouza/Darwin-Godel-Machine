import json
from typing import Dict, Any

def detect_attack(prompt: str, context: Dict[str, Any], model_runner: Any) -> Dict[str, Any]:
    system_prompt = """You are a security analyst. Analyze the prompt for agentic attacks.
    Respond ONLY with valid JSON: {"is_attack": bool, "attack_type": str, "confidence": float, "explanation": str}"""
    user_message = f"Analyze this prompt: {prompt}"
    formatted_prompt = f"Analyze this prompt: {system_prompt}\n\n{user_message}"
    
    try:
        response = model_runner(formatted_prompt, max_tokens=1000)
        response = response.strip()
        if "{" in response and "}" in response:
            response = response[response.find("{"):response.rfind("}")+1]
        return json.loads(response)
    except Exception as e:
        return {"is_attack": False, "attack_type": "error", "confidence": 0.0, "explanation": str(e)}