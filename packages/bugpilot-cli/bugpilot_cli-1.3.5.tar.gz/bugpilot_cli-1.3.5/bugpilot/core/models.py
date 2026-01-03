"""
AI Model Integration Layer
Wrapper for core/llm package
"""

from bugpilot.core.llm.base import BaseModel
from bugpilot.core.llm.gemini import GeminiModel
from bugpilot.core.llm.groq import GroqModel
from bugpilot.core.llm.ollama import OllamaModel
from bugpilot.core.llm.anthropic import AnthropicModel
from bugpilot.core.llm.factory import ModelFactory, get_model

__all__ = [
    'BaseModel',
    'GeminiModel',
    'GroqModel',
    'OllamaModel',
    'AnthropicModel',
    'ModelFactory',
    'get_model'
]
