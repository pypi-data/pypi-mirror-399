"""Anthropic Model Implementation"""

from typing import List, Dict, Optional
from .base import BaseModel

try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicModel(BaseModel):
    """Anthropic Claude model integration"""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        if anthropic:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Anthropic"""
        if not self.client:
            return "Error: Anthropic package not installed."
            
        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.kwargs.get('max_tokens', 4096),
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            return f"Anthropic Error: {str(e)}"
