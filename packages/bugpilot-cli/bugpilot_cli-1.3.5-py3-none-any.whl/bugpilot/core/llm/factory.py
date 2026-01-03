"""Model Factory"""

from typing import Optional
from .base import BaseModel
from .gemini import GeminiModel
from .groq import GroqModel
from .ollama import OllamaModel
from .anthropic import AnthropicModel


class ModelFactory:
    """Factory for creating AI model instances"""
    
    @staticmethod
    def create_model(provider: str, api_key: Optional[str] = None, model_name: str = None, **kwargs) -> BaseModel:
        """Create and return appropriate model instance"""
        
        models = {
            "gemini": (GeminiModel, "gemini-2.0-flash-exp"),
            "groq": (GroqModel, "llama-3.3-70b-versatile"),
            "ollama": (OllamaModel, "llama3.2"),
            "anthropic": (AnthropicModel, "claude-3-5-sonnet-20241022"),
        }
        
        provider = provider.lower()
        if provider not in models:
            provider = "gemini"
        
        model_class, default_model = models[provider]
        model_name = model_name or default_model
        
        if provider == "ollama":
            return model_class(model_name=model_name, **kwargs)
        else:
            return model_class(api_key=api_key, model_name=model_name, **kwargs)

def get_model(model_name: str = None, api_key: str = None, provider: str = "gemini", **kwargs) -> BaseModel:
    """Helper to get a model instance"""
    return ModelFactory.create_model(provider=provider, api_key=api_key, model_name=model_name, **kwargs)
