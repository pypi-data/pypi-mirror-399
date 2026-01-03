"""Interactive Settings Editor - Rich-based UI"""

import os
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box


class SettingsEditor:
    """Interactive settings editor with Rich UI"""
    
    def __init__(self):
        self.settings_path = Path(__file__).parent / "settings.yaml"
        self.console = Console()
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Load settings from package"""
        if not self.settings_path.exists():
            # Create from defaults
            defaults = Path(__file__).parent / "defaults.yaml"
            if defaults.exists():
                import shutil
                shutil.copy(defaults, self.settings_path)
        
        with open(self.settings_path, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def save_settings(self):
        """Save settings with error handling"""
        try:
            with open(self.settings_path, 'w') as f:
                yaml.dump(self.settings, f, default_flow_style=False, sort_keys=False)
            self.console.print("\n[green]Settings saved successfully![/green]")
        except PermissionError:
            self.console.print("\n[red]Error: Permission denied saving settings.yaml[/red]")
            self.console.print("[yellow]Try running as Administrator/Root to save package settings.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
        except Exception as e:
            self.console.print(f"\n[red]Error saving settings: {e}[/red]")
            Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def show_menu(self):
        """Main settings menu"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Title
            title = Panel.fit(
                "[bold cyan]BugPilot Settings[/bold cyan]\n[dim]Configure everything here[/dim]",
                border_style="cyan",
                box=box.DOUBLE
            )
            self.console.print(title)
            
            # Menu options
            table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
            table.add_column("Key", style="cyan")
            table.add_column("Option")
            
            table.add_row("1", "API Keys")
            table.add_row("2", "LLM Models & Parameters")
            table.add_row("3", "Safety & Limits")
            table.add_row("4", "Modes (Forge/Hacker)")
            table.add_row("5", "UI Preferences")
            table.add_row("6", "Context & Session")
            table.add_row("7", "View All Settings")
            table.add_row("s", "[green]Save & Return[/green]")
            table.add_row("x", "[yellow]Return without saving[/yellow]")
            
            self.console.print(table)
            
            choice = Prompt.ask("\n[cyan]Select[/cyan]", default="s")
            
            if choice == "1":
                self.edit_api_keys()
            elif choice == "2":
                self.edit_models()
            elif choice == "3":
                self.edit_safety()
            elif choice == "4":
                self.edit_modes()
            elif choice == "5":
                self.edit_ui()
            elif choice == "6":
                self.edit_context_session()
            elif choice == "7":
                self.view_all()
            elif choice.lower() == "s":
                self.save_settings()
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            elif choice.lower() == "x":
                if Confirm.ask("[yellow]Discard changes?[/yellow]"):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    break
    
    def edit_api_keys(self):
        """Edit API keys"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("[cyan]API Keys[/cyan]", border_style="cyan"))
        
        if 'api_keys' not in self.settings:
            self.settings['api_keys'] = {}
        
        providers = {
            '1': ('gemini', 'Gemini'),
            '2': ('groq', 'Groq'),
            '3': ('openai', 'OpenAI'),
            '4': ('claude', 'Claude (Anthropic)')
        }
        
        for key, (provider, name) in providers.items():
            current = self.settings['api_keys'].get(provider, '')
            status = "[green]Set[/green]" if current else "[red]Not set[/red]"
            self.console.print(f"\n{key}. {name}: {status}")
        
        self.console.print("\n[dim]Press Enter to skip[/dim]")
        
        for key, (provider, name) in providers.items():
            if Confirm.ask(f"\nSet {name} API key?", default=False):
                api_key = Prompt.ask(f"Enter {name} API key", password=True)
                if api_key:
                    self.settings['api_keys'][provider] = api_key
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def edit_models(self):
        """Edit model configuration"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("[cyan]LLM Configuration[/cyan]", border_style="cyan"))
        
        if 'llm' not in self.settings:
            self.settings['llm'] = {}
        
        # Default provider
        current_provider = self.settings['llm'].get('default_provider', 'gemini')
        self.console.print(f"\nCurrent provider: [yellow]{current_provider}[/yellow]")
        
        provider = Prompt.ask(
            "Default provider",
            choices=["gemini", "groq", "openai", "claude"],
            default=current_provider
        )
        self.settings['llm']['default_provider'] = provider
        
        # Parameters
        self.console.print("\n[cyan]Parameters:[/cyan]")
        
        temp = Prompt.ask(
            "Temperature (0.0 - 1.0)",
            default=str(self.settings['llm'].get('temperature', 0.7))
        )
        try:
            self.settings['llm']['temperature'] = float(temp)
        except ValueError:
            pass
            
        max_tokens = Prompt.ask(
            "Max Tokens",
            default=str(self.settings['llm'].get('max_tokens', 8192))
        )
        try:
            self.settings['llm']['max_tokens'] = int(max_tokens)
        except ValueError:
            pass

        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def edit_context_session(self):
        """Edit context and session settings"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("[cyan]Context & Session[/cyan]", border_style="cyan"))
        
        # Context
        if 'context' not in self.settings:
            self.settings['context'] = {}
            
        self.console.print("\n[yellow]Context Memory:[/yellow]")
        max_ctx = Prompt.ask(
            "Max Context Window (tokens)",
            default=str(self.settings['context'].get('max_tokens', 8000))
        )
        self.settings['context']['max_tokens'] = int(max_ctx)
        
        max_hist = Prompt.ask(
            "Max History Items",
            default=str(self.settings['context'].get('max_history', 50))
        )
        self.settings['context']['max_history'] = int(max_hist)
        
        # Session
        if 'session' not in self.settings:
            self.settings['session'] = {}
            
        self.console.print("\n[yellow]Session Management:[/yellow]")
        self.settings['session']['auto_save'] = Confirm.ask(
            "Auto-save sessions?",
            default=self.settings['session'].get('auto_save', True)
        )
        
        save_dir = Prompt.ask(
            "Session Save Directory",
            default=self.settings['session'].get('save_dir', '.bugpilot_sessions')
        )
        self.settings['session']['save_dir'] = save_dir
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def view_all(self):
        """View all settings"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("[cyan]Current Settings[/cyan]", border_style="cyan"))
        
        # Mask API keys
        display_settings = self.settings.copy()
        if 'api_keys' in display_settings:
            for key in display_settings['api_keys']:
                val = display_settings['api_keys'][key]
                if val:
                    display_settings['api_keys'][key] = val[:8] + "..." if len(val) > 8 else "***"
        
        self.console.print(yaml.dump(display_settings, default_flow_style=False))
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

    def edit_safety(self):
        """Edit safety settings"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("[cyan]Safety Settings[/cyan]", border_style="cyan"))
        
        if 'safety' not in self.settings:
            self.settings['safety'] = {}
        
        self.console.print("\n[yellow]1.[/yellow] Command Confirmation")
        self.settings['safety']['require_confirmation'] = Confirm.ask(
            "  Require confirmation before executing commands?",
            default=self.settings['safety'].get('require_confirmation', False)
        )
        
        self.console.print("\n[yellow]2.[/yellow] Limits")
        max_calls = Prompt.ask(
            "  Max tool calls per session",
            default=str(self.settings['safety'].get('max_tool_calls', 10))
        )
        self.settings['safety']['max_tool_calls'] = int(max_calls)
        
        timeout = Prompt.ask(
            "  Command timeout (seconds)",
            default=str(self.settings['safety'].get('timeout_seconds', 90))
        )
        self.settings['safety']['timeout_seconds'] = int(timeout)
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def edit_modes(self):
        """Edit mode configuration"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("[cyan]Modes Configuration[/cyan]", border_style="cyan"))
        
        if 'modes' not in self.settings:
            self.settings['modes'] = {}
        
        default_mode = Prompt.ask(
            "\nDefault mode",
            choices=["forge", "hacker"],
            default=self.settings['modes'].get('default', 'forge')
        )
        self.settings['modes']['default'] = default_mode
        
        # Forge mode
        if 'forge' not in self.settings['modes']:
            self.settings['modes']['forge'] = {}
        
        self.console.print("\n[cyan]Forge Mode Settings:[/cyan]")
        max_steps = Prompt.ask(
            "  Max steps",
            default=str(self.settings['modes']['forge'].get('max_steps', 3))
        )
        self.settings['modes']['forge']['max_steps'] = int(max_steps)
        
        # Hacker mode
        if 'hacker' not in self.settings['modes']:
            self.settings['modes']['hacker'] = {}
        
        self.console.print("\n[cyan]Hacker Mode Settings:[/cyan]")
        max_iter = Prompt.ask(
            "  Max iterations",
            default=str(self.settings['modes']['hacker'].get('max_iterations', 20))
        )
        self.settings['modes']['hacker']['max_iterations'] = int(max_iter)
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    
    def edit_ui(self):
        """Edit UI preferences"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(Panel("[cyan]UI Preferences[/cyan]", border_style="cyan"))
        
        if 'ui' not in self.settings:
            self.settings['ui'] = {}
        
        # Theme selection
        current_theme = self.settings['ui'].get('theme', 'ocean')
        self.console.print(f"\n[yellow]Current theme:[/yellow] [bold]{current_theme}[/bold]")
        theme = Prompt.ask(
            "\nSelect theme",
            choices=["ocean", "sunset", "neon", "forest", "midnight", "cyber", "minimal"],
            default=current_theme
        )
        self.settings['ui']['theme'] = theme
        
        self.settings['ui']['show_status_bar'] = Confirm.ask(
            "\nShow status bar?",
            default=self.settings['ui'].get('show_status_bar', True)
        )
        
        self.settings['ui']['typing_effect'] = Confirm.ask(
            "Enable typing effect?",
            default=self.settings['ui'].get('typing_effect', True)
        )
        
        if self.settings['ui']['typing_effect']:
            typing_speed = Prompt.ask(
                "Typing speed (characters per second)",
                default=str(self.settings['ui'].get('typing_speed', 150))
            )
            self.settings['ui']['typing_speed'] = int(typing_speed)
        
        self.settings['ui']['markdown_rendering'] = Confirm.ask(
            "Enable markdown rendering?",
            default=self.settings['ui'].get('markdown_rendering', True)
        )
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
    

