"""Pydantic schemas for configuration validation"""

from pydantic import BaseModel, Field
from typing import List, Optional


class LLMConfig(BaseModel):
    provider: str = "gemini"
    model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: int = 8192
    api_key: Optional[str] = None


class SafetyConfig(BaseModel):
    require_confirmation: bool = False
    dangerous_commands: List[str] = []
    max_tool_calls: int = 10


class ModesConfig(BaseModel):
    default: str = "forge"


class ContextConfig(BaseModel):
    max_tokens: int = 8000
    max_history: int = 50


class SessionConfig(BaseModel):
    auto_save: bool = True
    save_dir: str = ".bugpilot_sessions"


class BugPilotConfig(BaseModel):
    llm: LLMConfig
    safety: SafetyConfig
    modes: ModesConfig
    context: ContextConfig
    session: SessionConfig
