"""Base LLM Interface"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseModel(ABC):
    """Base class for all AI models"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = None, **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response from the model"""
        pass
