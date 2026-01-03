"""
Status Bar Component - Shows context, tokens, and progress
Part of BugPilot v1.4.0 UI Enhancement
"""

from rich.console import Console
from typing import Optional


class StatusBar:
    """Status bar showing real-time AI metrics"""
    
    def __init__(self, console: Console):
        self.console = console
        self.context_used = 0
        self.context_limit = 8096
        self.tokens_used = 0
        self.tokens_limit = 8192
        self.current_iteration = 0
        self.total_findings = 0
        self.current_phase = "IDLE"
        self.model_name = "Unknown"
        
    def update(self, **kwargs):
        """Update status bar metrics"""
        self.context_used = kwargs.get('context_used', self.context_used)
        self.tokens_used = kwargs.get('tokens_used', self.tokens_used)
        self.current_iteration = kwargs.get('iteration', self.current_iteration)
        self.total_findings = kwargs.get('findings', self.total_findings)
        self.current_phase = kwargs.get('phase', self.current_phase)
        self.model_name = kwargs.get('model', self.model_name)
        
    def get_toolbar_content(self, mode: str) -> str:
        """Get HTML content for prompt_toolkit bottom toolbar"""
        import datetime
        
        # Calculate percentages
        tokens_pct = int((self.tokens_used / self.tokens_limit) * 100) if self.tokens_limit else 0
        
        time_str = datetime.datetime.now().strftime("%H:%M")
        
        # Clean Model Name (shorten if needed)
        display_model = self.model_name
        if len(display_model) > 40:
            display_model = display_model[:37] + ".."
            
        # Construct the content string with double spaces for clean separation
        # Format: [ MODE ]  PHASE  Model  Tokens  Findings  Time
        
        content = (
            f"[ {mode.upper()} ]  "
            f"{self.current_phase}  "
            f"{display_model}  "
            f"Tokens: {self.tokens_used}/{self.tokens_limit}  "
            f"Findings: {self.total_findings}  "
            f"{time_str}"
        )
        
        # Calculate centering padding
        try:
            width = self.console.width
            padding_len = max(0, (width - len(content)) // 2)
            padding = " " * padding_len
        except:
             padding = ""
             
        # Single style: Black background, White text
        # Using pure simple styling
        return f'<style bg="#000000" fg="#ffffff">{padding}{content}{padding}</style>'


class ProgressIndicator:
    """Live progress indicator for operations"""
    
    def __init__(self, console: Console):
        self.console = console
        
    def show_scanning(self, target: str, progress: int = 0):
        """Show scanning progress"""
        bar = self._make_bar(progress)
        self.console.print(
            f"\n[cyan][SCANNING][/] {bar} {progress}% | Target: {target}",
            end="\r"
        )
    
    def show_testing(self, vuln_type: str, progress: int = 0):
        """Show testing progress"""
        bar = self._make_bar(progress)
        self.console.print(
            f"\n[yellow][TESTING][/] {bar} {progress}% | {vuln_type}",
            end="\r"
        )
    
    def show_exploiting(self, target: str):
        """Show exploitation in progress"""
        self.console.print(
            f"\n[red][EXPLOITING][/] {target}...",
            style="bold"
        )
    
    def _make_bar(self, progress: int, width: int = 20) -> str:
        """Create a simple progress bar"""
        filled = int((progress / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return bar


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    return len(text) // 4
