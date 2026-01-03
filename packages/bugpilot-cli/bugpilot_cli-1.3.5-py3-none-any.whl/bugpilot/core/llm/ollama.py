"""Ollama Model Implementation"""

import httpx
from typing import List, Dict
from .base import BaseModel


class OllamaModel(BaseModel):
    """Ollama local model integration"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(None, model_name, **kwargs)
        self.base_url = base_url
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            
            full_prompt = prompt
            if context:
                for msg in context:
                    full_prompt = f"{msg['role']}: {msg['content']}\n" + full_prompt

            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False
            }
            
            response = httpx.post(url, json=payload, timeout=60.0)
            return response.json().get("response", "No response")
        except Exception as e:
            return f"Ollama Error: {str(e)}"
