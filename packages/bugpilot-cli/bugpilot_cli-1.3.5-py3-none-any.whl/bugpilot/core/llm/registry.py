"""LLM Registry - Routes requests to appropriate providers"""

from typing import Dict, Type
from .base import BaseLLM
from .gemini import GeminiLLM


class LLMRegistry:
    """Central registry for LLM providers"""
    
    _providers: Dict[str, Type[BaseLLM]] = {
        "gemini": GeminiLLM,
    }
    
    @classmethod
    def register(cls, name: str, provider: Type[BaseLLM]):
        """Register a new LLM provider"""
        cls._providers[name] = provider
    
    @classmethod
    def get(cls, name: str, model: str, api_key: str, **kwargs) -> BaseLLM:
        """Get LLM instance by provider name"""
        provider_class = cls._providers.get(name)
        if not provider_class:
            raise ValueError(f"Unknown LLM provider: {name}")
        
        return provider_class(model, api_key, **kwargs)
    
    @classmethod
    def create_from_config(cls, config) -> Dict[str, BaseLLM]:
        """Create LLM instances for different tasks from config"""
        # For now, use same model for all tasks
        # Can be extended to use different models per task
        api_key = config.llm.api_key
        
        llm = cls.get(
            config.llm.provider,
            config.llm.model,
            api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens
        )
        
        return {
            "intent": llm,
            "reasoning": llm,
            "execution": llm,
            "reporting": llm
        }
