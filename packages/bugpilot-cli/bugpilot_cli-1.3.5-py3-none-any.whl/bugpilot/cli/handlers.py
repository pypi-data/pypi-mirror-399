"""
Command Handler for BugPilot CLI
Professional command system like Claude CLI and Gemini CLI
"""

from typing import Dict, List, Optional, Callable
from pathlib import Path
import json


class CommandHandler:
    """Handles all CLI commands like professional AI CLIs"""
    
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.commands = self._register_commands()
        self.session_manager = None
        self.file_exporter = None
        
    def _register_commands(self) -> Dict[str, dict]:
        """Register all available commands"""
        return {
            "/help": {
                "handler": self.cmd_help,
                "description": "Show all available commands",
                "usage": "/help [command]"
            },
            "/save": {
                "handler": self.cmd_save,
                "description": "Save results to file",
                "usage": "/save <filename> [format]"
            },
            "/export": {
                "handler": self.cmd_export,
                "description": "Export session to file",
                "usage": "/export <filename> <format>"
            },
            "/sessions": {
                "handler": self.cmd_sessions,
                "description": "List all saved sessions",
                "usage": "/sessions"
            },
            "/load": {
                "handler": self.cmd_load,
                "description": "Load a previous session",
                "usage": "/load <session_id>"
            },
            "/clear": {
                "handler": self.cmd_clear,
                "description": "Clear screen",
                "usage": "/clear"
            },
            "/history": {
                "handler": self.cmd_history,
                "description": "Show command history",
                "usage": "/history"
            },
            "/settings": {
                "handler": self.cmd_settings,
                "description": "Interactive settings editor",
                "usage": "/settings [show|edit|set|toggle|export|import|reset]"
            },
            "/model": {
                "handler": self.cmd_model,
                "description": "Switch AI model",
                "usage": "/model <provider> <model>"
            },
            "/output": {
                "handler": self.cmd_output,
                "description": "Set output directory",
                "usage": "/output <path>"
            },
            "/autopilot": {
                "handler": self.cmd_autopilot,
                "description": "Toggle autonomous mode",
                "usage": "/autopilot [on|off]"
            },
            "/autopilot": {
                "handler": self.cmd_autopilot,
                "description": "Toggle autonomous mode",
                "usage": "/autopilot [on|off]"
            },
            "/stream": {
                "handler": self.cmd_stream,
                "description": "Toggle streaming mode",
                "usage": "/stream [on|off]"
            },
            "/tokens": {
                "handler": self.cmd_tokens,
                "description": "Show token usage",
                "usage": "/tokens"
            },
            "/reset": {
                "handler": self.cmd_reset,
                "description": "Reset current session",
                "usage": "/reset"
            },
            "/exit": {
                "handler": self.cmd_exit,
                "description": "Exit BugPilot",
                "usage": "/exit"
            },
            "/quit": {
                "handler": self.cmd_exit,
                "description": "Alias for /exit",
                "usage": "/quit"
            },
            "/update": {
                "handler": self.cmd_update,
                "description": "Check and install updates",
                "usage": "/update [check|install]"
            },
            "/cve": {
                "handler": self.cmd_cve,
                "description": "Look up CVE information",
                "usage": "/cve <CVE-ID> or /cve search <product> [version]"
            },
            "/owasp": {
                "handler": self.cmd_owasp,
                "description": "Get OWASP Top 10 information",
                "usage": "/owasp [item-id] or /owasp search <keyword>"
            }
        }
    
    def handle(self, command: str) -> bool:
        """Handle a command. Returns True if command was handled"""
        if not command.startswith('/'):
            return False
            
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            try:
                self.commands[cmd]["handler"](args)
                return True
            except Exception as e:
                self.cli.ui.print_error(f"Command error: {str(e)}")
                return True
        else:
            self.cli.ui.print_error(f"Unknown command: {cmd}. Type /help for available commands.")
            return True
    
    def cmd_help(self, args: List[str]):
        """Show help"""
        if args:
            cmd = args[0] if args[0].startswith('/') else f'/{args[0]}'
            if cmd in self.commands:
                info = self.commands[cmd]
                self.cli.ui.print_panel(
                    f"**{cmd}**\n\n{info['description']}\n\nUsage: `{info['usage']}`",
                    title="Command Help",
                    style="info"
                )
            else:
                self.cli.ui.print_error(f"Unknown command: {cmd}")
        else:
            from rich.table import Table
            from rich import box
            
            # Create a nice table for commands
            table = Table(
                title="[!] BugPilot CLI Commands",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan",
                border_style="cyan",
                padding=(0, 1)
            )
            
            table.add_column("Command", style="yellow bold", width=15)
            table.add_column("Description", style="white", width=50)
            
            # Add commands to table
            for cmd, info in sorted(self.commands.items()):
                table.add_row(cmd, info['description'])
            
            self.cli.ui.console.print("\n")
            self.cli.ui.console.print(table)
            self.cli.ui.console.print("\n[dim][+] Type [cyan]/help <command>[/cyan] for detailed usage[/dim]\n")
    
    def cmd_save(self, args: List[str]):
        """Save results to file"""
        if not args:
            self.cli.ui.print_error("Usage: /save <filename> [format]")
            return
            
        filename = args[0]
        format_type = args[1] if len(args) > 1 else "txt"
        
        if not self.session_manager or not self.session_manager.current_session:
            self.cli.ui.print_error("No active session to save")
            return
        
        # Export current session
        success = self.session_manager.export_results(filename, format_type)
        if success:
            self.cli.ui.print_success(f"Results saved to: {filename}")
        else:
            self.cli.ui.print_error("Failed to save results")
    
    def cmd_export(self, args: List[str]):
        """Export session"""
        if len(args) < 2:
            self.cli.ui.print_error("Usage: /export <filename> <format>")
            return
        
        filename, format_type = args[0], args[1]
        self.cmd_save([filename, format_type])
    
    def cmd_sessions(self, args: List[str]):
        """List all sessions"""
        if not self.session_manager:
            self.cli.ui.print_error("Session manager not available")
            return
        
        sessions = self.session_manager.list_sessions()
        if not sessions:
            self.cli.ui.print_info("No saved sessions found")
            return
        
        sessions_text = "**Saved Sessions:**\n\n"
        for session in sessions[-10:]:  # Last 10
            sessions_text += f"**{session['id']}**\n"
            sessions_text += f"  Objective: {session['objective'][:60]}...\n"
            sessions_text += f"  Created: {session['created_at']}\n"
            sessions_text += f"  Iterations: {session['iterations']}\n\n"
        
        self.cli.ui.print_panel(sessions_text, title="Sessions", style="info")
    
    def cmd_load(self, args: List[str]):
        """Load a session"""
        if not args:
            self.cli.ui.print_error("Usage: /load <session_id>")
            return
        
        session_id = args[0]
        if self.session_manager:
            session = self.session_manager.load_session(session_id)
            if session:
                self.cli.ui.print_success(f"Loaded session: {session_id}")
            else:
                self.cli.ui.print_error(f"Session not found: {session_id}")
    
    def cmd_clear(self, args: List[str]):
        """Clear screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def cmd_history(self, args: List[str]):
        """Show command history"""
        # TODO: Implement command history tracking
        self.cli.ui.print_info("Command history feature coming soon")
    
    def cmd_settings(self, args: List[str]):
        """Unified settings/config editor"""
        import os
        from bugpilot.core.config.editor import SettingsEditor
        
        # Save current theme
        old_theme = None
        if hasattr(self.cli, 'config_manager'):
            old_theme = self.cli.config_manager.config.get('ui', {}).get('theme', 'ocean')
        
        # New editor handles everything
        editor = SettingsEditor()
        editor.show_menu()
        
        # Reload config after edit
        if hasattr(self.cli, 'config_manager') and hasattr(self.cli.config_manager, 'load'):
            self.cli.config_manager.load()
            
            # Check if theme changed
            new_theme = self.cli.config_manager.config.get('ui', {}).get('theme', 'ocean')
            if new_theme != old_theme:
                # Reload UI with new theme
                from bugpilot.core.terminal_ui import TerminalUI
                self.cli.ui = TerminalUI(theme=new_theme)
                self.cli.ui.print_success(f"Theme changed to: {new_theme}")
        
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def cmd_model(self, args: List[str]):
        """Switch AI model"""
        if len(args) < 2:
            self.cli.ui.print_error("Usage: /model <provider> <model>")
            return
        
        provider, model = args[0], args[1]
        # Use config_manager if available
        if hasattr(self.cli, 'config_manager'):
            self.cli.config_manager.update_model(provider, model)
            self.cli.config_manager.save_config()
        self.cli.ui.print_success(f"Switched to: {provider}/{model}")
    
    def cmd_output(self, args: List[str]):
        """Set output directory"""
        if not args:
            if self.file_exporter:
                self.cli.ui.print_info(f"Current output: {self.file_exporter.get_output_dir()}")
            return
        
        path = args[0]
        if self.file_exporter:
            self.file_exporter.set_output_dir(path)
            self.cli.ui.print_success(f"Output directory set to: {path}")
    
    def cmd_stream(self, args: List[str]):
        """Toggle streaming"""
        # TODO: Implement streaming mode
        self.cli.ui.print_info("Streaming mode toggle coming soon")
    
    def cmd_tokens(self, args: List[str]):
        """Show token usage"""
        # TODO: Implement token counting
        self.cli.ui.print_info("Token usage tracking coming soon")
    
    def cmd_reset(self, args: List[str]):
        """Reset session"""
        if self.cli.ui.confirm("Reset current session?"):
            # TODO: Implement session reset
            self.cli.ui.print_success("Session reset")
    
    def cmd_exit(self, args: List[str]):
        """Exit CLI"""
        self.cli.running = False
        self.cli.ui.print_info("Goodbye!")
        
    def cmd_autopilot(self, args: List[str]):
        """Toggle autopilot"""
        new_val = False
        current = False
        
        # Access config dict
        if hasattr(self.cli, 'config_manager'):
            current = self.cli.config_manager.config.get('auto_execute_commands', False)
        
        if not args:
            new_val = not current
        else:
            new_val = args[0].lower() == 'on'
            
        if hasattr(self.cli, 'config_manager'):
             self.cli.config_manager.config['auto_execute_commands'] = new_val
             self.cli.config_manager.save_config()
             
        state = "ON" if new_val else "OFF"
        self.cli.ui.print_success(f"Autopilot mode: {state}")
    
    def cmd_update(self, args: List[str]):
        """Check for updates and install"""
        from bugpilot.core.updater import check_for_updates, update_package, get_latest_version, CURRENT_VERSION
        
        # Check for updates
        if not args:
            self.cli.ui.print_info(f"Current version: {CURRENT_VERSION}")
            self.cli.ui.print_info("Checking for updates...")
            
            latest = check_for_updates()
            if latest:
                self.cli.ui.print_success(f"[!] New version available: {latest}")
                if self.cli.ui.confirm("Install update now?"):
                    success = update_package(self.cli.ui)
                    if success:
                        self.cli.ui.print_warning("[!] Please restart BugPilot to use the new version")
            else:
                self.cli.ui.print_success("✓ You're running the latest version!")
                
        elif args[0] == "check":
            self.cli.ui.print_info(f"Current version: {CURRENT_VERSION}")
            self.cli.ui.print_info("Checking for updates...")
            latest = check_for_updates()
            if latest:
                self.cli.ui.print_success(f"[!] New version available: {latest}")
            else:
                self.cli.ui.print_success("✓ You're running the latest version!")
                
        elif args[0] == "install":
            # Confirm before updating
            if self.cli.ui.confirm("Update BugPilot CLI to the latest version?"):
                success = update_package(self.cli.ui)
                if success:
                    self.cli.ui.print_warning("[!] Please restart BugPilot to use the new version")
        else:
            self.cli.ui.print_error("Usage: /update [check|install]")
    
    def cmd_cve(self, args: List[str]):
        """Look up CVE information"""
        from bugpilot.tools import get_cve_info, search_cves_for_product
        
        if not args:
            self.cli.ui.print_error("Usage: /cve <CVE-ID> or /cve search <product> [version]")
            return
        
        if args[0].lower() == "search":
            if len(args) < 2:
                self.cli.ui.print_error("Usage: /cve search <product> [version]")
                return
            
            product = args[1]
            version = args[2] if len(args) > 2 else None
            
            self.cli.ui.print_info(f"Searching CVEs for {product} {version or ''}...")
            result = search_cves_for_product(product, version)
            self.cli.ui.print_panel(result, title="CVE Search Results", style="info")
        else:
            cve_id = args[0].upper()
            if not cve_id.startswith("CVE-"):
                cve_id = f"CVE-{cve_id}"
            
            self.cli.ui.print_info(f"Looking up {cve_id}...")
            result = get_cve_info(cve_id)
            self.cli.ui.print_panel(result, title=f"CVE Information: {cve_id}", style="warning")
    
    def cmd_owasp(self, args: List[str]):
        """Get OWASP Top 10 information"""
        from bugpilot.tools import get_owasp_info, search_owasp_vulnerability
        
        if not args:
            # Show all OWASP Top 10
            result = get_owasp_info()
            self.cli.ui.print_panel(result, title="OWASP Top 10 2021", style="info")
        elif args[0].lower() == "search":
            if len(args) < 2:
                self.cli.ui.print_error("Usage: /owasp search <keyword>")
                return
            
            keyword = " ".join(args[1:])
            result = search_owasp_vulnerability(keyword)
            self.cli.ui.print_panel(result, title=f"OWASP Search: {keyword}", style="info")
        else:
            item_id = args[0].upper()
            result = get_owasp_info(item_id)
            self.cli.ui.print_panel(result, title=f"OWASP Top 10: {item_id}", style="warning")
