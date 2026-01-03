"""Prompts Package"""

from bugpilot.core.utils.os_detection import OS_INFO
from .common import get_os_context
from .hacker import HACKER_MODE_PROMPT, HACKER_WELCOME
from .normal import NORMAL_MODE_PROMPT, NORMAL_WELCOME
from .tools import TOOL_SELECTION_PROMPT

def get_system_prompt(mode: str) -> str:
    """Retrieve system prompt based on mode with OS context"""
    os_context = get_os_context(OS_INFO)
    
    if mode.lower() == "hacker":
        return HACKER_MODE_PROMPT.format(os_context=os_context, 
                                       previous_findings="{previous_findings}", 
                                       current_iteration="{current_iteration}",
                                       max_iterations="{max_iterations}",
                                       actions_count="{actions_count}",
                                       tools="{tools}",
                                       failures="{failures}")
    else:
        return NORMAL_MODE_PROMPT.format(os_context=os_context)

def get_welcome_message(mode: str) -> str:
    """Return welcome message based on mode"""
    if mode.lower() == "hacker":
        return HACKER_WELCOME
    else:
        return NORMAL_WELCOME

__all__ = ['get_system_prompt', 'get_welcome_message', 'TOOL_SELECTION_PROMPT']
