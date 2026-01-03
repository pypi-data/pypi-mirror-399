"""Groq Model Implementation"""

from typing import List, Dict, Optional
from .base import BaseModel

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqModel(BaseModel):
    """Groq model integration"""
    
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        if Groq:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Groq"""
        if not self.client:
            return "Error: Groq package not installed."
            
        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.kwargs.get('temperature', 0.7),
                max_tokens=self.kwargs.get('max_tokens', 4096)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {str(e)}"
