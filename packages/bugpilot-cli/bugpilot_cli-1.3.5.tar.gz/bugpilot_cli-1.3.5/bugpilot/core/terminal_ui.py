"""
Rich Terminal UI with multiple modern themes
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich import box
from rich.text import Text
from rich.align import Align
import pyfiglet
from typing import Optional


class TerminalUI:
    """Advanced terminal UI with modern theming support"""
    
    THEMES = {
        "ocean": {
            "primary": "#00d4ff",
            "secondary": "#0099ff", 
            "accent": "#00ffcc",
            "success": "#00ff88",
            "warning": "#ffaa00",
            "error": "#ff3366",
            "info": "#00d4ff",
            "text": "#e0e0e0",
            "dim": "#888888",
            "bg": "#0a0e27",
        },
        "sunset": {
            "primary": "#ff6b6b",
            "secondary": "#ffa500",
            "accent": "#ff1744",
            "success": "#4caf50",
            "warning": "#ffc107",
            "error": "#f44336",
            "info": "#ff9800",
            "text": "#f5f5f5",
            "dim": "#757575",
            "bg": "#1a0a0a",
        },
        "neon": {
            "primary": "#ff00ff",
            "secondary": "#00ffff",
            "accent": "#39ff14",
            "success": "#00ff00",
            "warning": "#ffff00",
            "error": "#ff0055",
            "info": "#00ffff",
            "text": "#ffffff",
            "dim": "#666666",
            "bg": "#000000",
        },
        "forest": {
            "primary": "#00ff7f",
            "secondary": "#32cd32",
            "accent": "#7fff00",
            "success": "#00ff00",
            "warning": "#ffd700",
            "error": "#ff4500",
            "info": "#00fa9a",
            "text": "#f0fff0",
            "dim": "#556b2f",
            "bg": "#0d1b0d",
        },
        "midnight": {
            "primary": "#9d4edd",
            "secondary": "#5a67d8",
            "accent": "#c77dff",
            "success": "#06ffa5",
            "warning": "#ffc857",
            "error": "#ef476f",
            "info": "#7209b7",
            "text": "#f8f9fa",
            "dim": "#6c757d",
            "bg": "#0b0014",
        },
        "cyber": {
            "primary": "#00ffff",
            "secondary": "#ff00ff",
            "accent": "#ffff00",
            "success": "#00ff41",
            "warning": "#ff9500",
            "error": "#ff0055",
            "info": "#00d4ff",
            "text": "#e0ffe0",
            "dim": "#808080",
            "bg": "#000a0a",
        },
        "minimal": {
            "primary": "#ffffff",
            "secondary": "#cccccc",
            "accent": "#999999",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "info": "#2196f3",
            "text": "#e0e0e0",
            "dim": "#757575",
            "bg": "#121212",
        }
    }
    
    def __init__(self, theme: str = "ocean"):
        self.console = Console()
        self.theme = self.THEMES.get(theme, self.THEMES["ocean"])
    
    def show_banner(self, mode: str = "normal"):
        """Display clean, responsive banner"""
        import shutil
        
        # Get terminal width
        term_width = shutil.get_terminal_size().columns
        
        # Clean, minimal banner
        title = "BUGPILOT-CLI"
        subtitle = "AI-Powered Autonomous Penetration Testing"
        
        # Mode setup
        mode_icon = "[!]" if mode == "hacker" else "[+]"
        mode_text = "HACKER MODE" if mode == "hacker" else "NORMAL MODE"
        mode_color = self.theme['error'] if mode == 'hacker' else self.theme['success']
        
        # Print styled header
        self.console.print()
        self.console.rule(f"[{self.theme['primary']} bold]{title}[/]", style=self.theme['primary'])
        
        # Info line
        info_parts = [
            (subtitle, self.theme['secondary']),
            (" | ", self.theme['dim']),
            (f"{mode_icon} {mode_text}", mode_color),
        ]
        
        info_line = Text()
        for text, style in info_parts:
            info_line.append(text, style=f"bold {style}" if "MODE" in text else style)
        
        self.console.print(Align.center(info_line))
        
        # Developer credit
        dev_line = Text()
        dev_line.append("Developer: ", style=self.theme['dim'])
        dev_line.append("LAKSHMIKANTHAN K ", style=f"bold {self.theme['secondary']}")
        dev_line.append("(letchupkt)", style=self.theme['accent'])
        
        self.console.print(Align.center(dev_line))
        self.console.rule(style=self.theme['primary'])
        self.console.print()
    
    def print_message(self, message: str, style: str = "text"):
        """Print colored message"""
        color = self.theme.get(style, self.theme["text"])
        self.console.print(f"[{color}]{message}[/]")
    
    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"[{self.theme['success']}][+][/] {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"[{self.theme['error']}][-][/] {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"[{self.theme['warning']}][!][/] {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"[{self.theme['info']}][i][/] {message}")
    
    def print_markdown(self, markdown_text: str):
        """Print markdown formatted text"""
        md = Markdown(markdown_text)
        self.console.print(md)
    
    def print_code(self, code: str, language: str = "python"):
        """Print syntax-highlighted code"""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(syntax)
    
    def print_panel(self, content: str, title: str = "", style: str = "primary"):
        """Print content in a panel using Markdown rendering"""
        from rich.markdown import Markdown
        from rich import box
        
        # Render markdown if content is string
        if isinstance(content, str):
            renderable = Markdown(content)
        else:
            renderable = content
            
        # Get border style from theme if available, otherwise use raw style
        border_style = self.theme.get(style, style)
            
        panel = Panel(
            renderable,
            title=title,
            border_style=border_style,
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def create_table(self, title: str, columns: list) -> Table:
        """Create a rich table"""
        table = Table(
            title=title,
            border_style=self.theme['primary'],
            header_style=f"bold {self.theme['secondary']}"
        )
        
        for col in columns:
            table.add_column(col)
        
        return table
    
    def prompt(self, message: str, default: str = "") -> str:
        """Get user input with prompt"""
        return Prompt.ask(
            f"[{self.theme['primary']}]{message}[/]",
            default=default,
            show_default=bool(default)
        )
    
    def confirm(self, message: str) -> bool:
        """Get yes/no confirmation"""
        return Confirm.ask(f"[{self.theme['warning']}]{message}[/]")
    
    def show_settings_menu(self, config):
        """Display settings in a formatted table"""
        table = Table(
            title="[*] BugPilot Settings",
            border_style=self.theme['primary'],
            box=box.DOUBLE_EDGE
        )
        
        table.add_column("Setting", style=self.theme['secondary'])
        table.add_column("Value", style=self.theme['text'])
        
        table.add_row("AI Provider", config.model.provider)
        table.add_row("Model Name", config.model.model_name)
        table.add_row("Operating Mode", config.mode.upper())
        table.add_row("Temperature", str(config.model.temperature))
        table.add_row("Max Tokens", str(config.model.max_tokens))
        table.add_row("MCP Enabled", "Yes" if config.mcp_enabled else "No")
        table.add_row("Theme", config.terminal_theme)
        table.add_row("Auto Execute", "Yes" if config.auto_execute_commands else "No")
        table.add_row("Context History", str(config.context_history_size))
        
        self.console.print(table)
    
    def show_model_options(self):
        """Show available AI models"""
        table = Table(
            title="[AI] Available AI Models",
            border_style=self.theme['primary'],
            box=box.ROUNDED
        )
        
        table.add_column("Provider", style=f"bold {self.theme['secondary']}")
        table.add_column("Models", style=self.theme['text'])
        table.add_column("Status", style=self.theme['info'])
        
        table.add_row(
            "Gemini", 
            "gemini-2.0-flash-exp, gemini-2.0-flash-thinking-exp,\ngemini-1.5-pro, gemini-1.5-flash", 
            "[+] Latest"
        )
        table.add_row(
            "gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo", 
            "[+] Available"
        )
        table.add_row(
            "Groq", 
            "llama-3.3-70b-versatile, mixtral-8x7b-32768,\nllama-3.1-70b-versatile", 
            "[+] Fast"
        )
        table.add_row(
            "Ollama", 
            "llama3.2, qwen2.5, deepseek-coder, mistral", 
            "[+] Local"
        )
        table.add_row(
            "Anthropic", 
            "claude-3-5-sonnet, claude-3-opus, claude-3-sonnet", 
            "[+] Available"
        )
        
        self.console.print(table)
    
    def show_help(self, mode: str):
        """Show help information"""
        import os
        help_text = f"""
# BugPilot CLI Commands

## General Commands:
- `/help` - Show this help message
- `/settings` - View current settings
- `/configure` - Configure AI model and settings
- `/mode [normal|hacker]` - Switch operating mode
- `/clear` - Clear conversation context
- `/exit` or `/quit` - Exit BugPilot

## File System Commands:
- `list files` or `ls` - List files in current directory
- `read file "filename"` - Read and display file contents
- `analyze project` - Analyze project structure and languages
- `show structure` - Display directory tree

## Mode-Specific Features:

### Normal Mode:
- Ask questions about security concepts
- Request code generation and scripts
- Get command suggestions
- Security analysis and reviews
- File reading and analysis

### Hacker Mode:
- Autonomous penetration testing
- Real-time command execution
- Target reconnaissance and enumeration
- Vulnerability scanning and exploitation
- File system access for analysis

## Available Themes:
- **Ocean** (default) - Cool cyan and blue tones
- **Sunset** - Warm oranges and reds
- **Neon** - Bright cyberpunk colors
- **Forest** - Green natural tones
- **Midnight** - Purple and dark blue

## Current Mode: **{mode.upper()}**
## Current Directory: {os.getcwd()}

Type your question or command to begin!
"""
        self.print_markdown(help_text)
    
    def loading_indicator(self, message: str = "Processing..."):
        """Show loading indicator context manager"""
        return self.console.status(
            f"[{self.theme['primary']}]{message}[/]",
            spinner="dots"
        )

    def type_text(self, text: str, speed: float = 0.005):
        """Typing effect for markdown text"""
        from rich.live import Live
        from rich.markdown import Markdown
        import time
        from rich.panel import Panel
        from rich import box
        
        # Determine style based on last used theme or default
        style = self.theme['primary']
        
        current_text = ""
        
        # Create a container panel that grows
        def render_panel(txt):
            return Panel(
                Markdown(txt),
                border_style=style,
                box=box.ROUNDED,
                title="[AI] BugPilot",
                title_align="left"
            )
            
        with Live(render_panel(""), refresh_per_second=20, console=self.console) as live:
             for char in text:
                 current_text += char
                 # Update periodically to reduce flicker and CPU load
                 if char in ['\n', ' ', '.', '!', '?'] or len(current_text) % 5 == 0:
                     live.update(render_panel(current_text))
                     time.sleep(speed)
             live.update(render_panel(current_text))

    def get_input(self, message: str, bottom_toolbar_func=None) -> str:
        """Get input using prompt_toolkit with optional bottom toolbar and autocomplete"""
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.styles import Style
            from prompt_toolkit.formatted_text import HTML
            from bugpilot.cli.autocomplete import BugPilotCompleter
            
            # Simple style derived from theme
            style = Style.from_dict({
                'bottom-toolbar': f"bg:{self.theme['bg']} fg:{self.theme['secondary']}",
            })
            
            # Initialize completer for commands (/) and files (@)
            completer = BugPilotCompleter()
            
            session = PromptSession(completer=completer)
            
            # Use HTML prompt for colors
            # Strip brackets from theme color to get hex
            color_hex = self.theme['primary'].replace('#', '')
            formatted_prompt = HTML(f"<b><style fg='#{color_hex}'>{message} </style></b>")
            
            return session.prompt(formatted_prompt, bottom_toolbar=bottom_toolbar_func, style=style)
            
        except ImportError:
            # Fallback to rich prompt if prompt_toolkit not available
            return self.prompt(message)
    
    def get_input_with_status(self, message: str, status_bar_callback) -> str:
        """Helper to get input with status bar"""
        from prompt_toolkit.formatted_text import HTML
        
        def get_toolbar():
            if status_bar_callback:
                content = status_bar_callback()
                return HTML(content)
            return ""
            
        return self.get_input(message, bottom_toolbar_func=get_toolbar)


