"""BugPilot CLI - Main Entry Point with Full Features"""

import sys
import os
from pathlib import Path
from types import SimpleNamespace

# Fix imports if run as script
if __package__ is None:
    sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Main entry point integrating old UI with new backend"""
    
    # 1. Initialize Configuration
    from bugpilot.core.config.settings import ConfigManager
    config_mgr = ConfigManager()
    
    # 2. Initialize UI with theme from config
    from bugpilot.core.terminal_ui import TerminalUI
    theme = config_mgr.config.get('ui', {}).get('theme', 'ocean')
    ui = TerminalUI(theme=theme)
    
    # Clean screen on startup
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 3. Initialize Status Bar
    from bugpilot.core.status_bar import StatusBar
    status_bar = StatusBar(ui.console)
    
    # Check for API key
    if not config_mgr.has_api_key():
        ui.console.print("\n[yellow]⚠ No API key configured[/yellow]")
        ui.console.print("[cyan]Press 's' to open settings, or add API key to environment[/cyan]\n")
        
        choice = ui.prompt("Continue? (s=settings, enter=skip): ").strip().lower()
        if choice == 's':
            from bugpilot.core.config.editor import SettingsEditor
            SettingsEditor().show_menu()
            config_mgr.load() # Reload config
            # Reload UI with new theme
            new_theme = config_mgr.config.get('ui', {}).get('theme', 'ocean')
            ui = TerminalUI(theme=new_theme)
            status_bar = StatusBar(ui.console)
            # Clean screen again
            os.system('cls' if os.name == 'nt' else 'clear')
    
    config = config_mgr.config
    
    # Check for updates (non-blocking)
    try:
        from bugpilot.core.updater import check_for_updates, show_update_notification
        latest_version = check_for_updates()
        if latest_version:
            show_update_notification(ui, latest_version)
    except Exception:
        pass  # Silently fail if update check doesn't work
    
    # 4. Setup CLI Wrapper for CommandHandler
    class BugPilotCLI:
        def __init__(self, ui, config_mgr):
            self.ui = ui
            self.config_manager = config_mgr
            self.running = True
            
            # Session Manager
            try:
                from bugpilot.core.state.session import SessionManager
                self.session_manager = SessionManager()
            except ImportError:
                self.session_manager = None
                
            # File Exporter (Basic implementation)
            class SimpleFileExporter:
                def __init__(self):
                    self.output_dir = Path("output")
                    self.output_dir.mkdir(exist_ok=True)
                def set_output_dir(self, path):
                    self.output_dir = Path(path)
                    self.output_dir.mkdir(exist_ok=True)
                def get_output_dir(self):
                    return str(self.output_dir)
            self.file_exporter = SimpleFileExporter()

    cli_app = BugPilotCLI(ui, config_mgr)
    
    # 5. Initialize Command Handler
    from bugpilot.cli.handlers import CommandHandler
    cmd_handler = CommandHandler(cli_app)
    
    # Link managers to handler
    cmd_handler.session_manager = cli_app.session_manager
    cmd_handler.file_exporter = cli_app.file_exporter

    # 6. Initialize Agent
    # Load default mode from config (modes -> default) or fallback to 'normal'
    default_mode = config.get('modes', {}).get('default', 'normal')
    mode = os.getenv('BUGPILOT_MODE', default_mode) 
    
    # Ensure mode is valid
    if mode not in ['normal', 'hacker']:
        mode = 'normal'
        
    ui.show_banner(mode)

    # Agent setup
    from bugpilot.core.llm.factory import get_model
    from bugpilot.agent.controller import Controller
    from bugpilot.modes.hacker import HackerMode
    from bugpilot.modes.forge import ForgeMode
    
    controller = None
    agent_available = False
    model_name = "Unknown"
    
    try:
        provider = config.get('llm', {}).get('default_provider', 'gemini')
        # Try to safely get deep key
        model_name = "gemini-2.0-flash-exp"
        if isinstance(config.get('llm'), dict):
             models_cfg = config['llm'].get('models', {})
             if models_cfg and isinstance(models_cfg, dict):
                 reasoning_cfg = models_cfg.get('reasoning', {})
                 if reasoning_cfg:
                     model_name = reasoning_cfg.get('model', model_name)
        
        api_key = config_mgr.get_api_key(provider)
        
        if api_key or provider == 'ollama':
            # Create models
            reasoning_llm = get_model(model_name=model_name, api_key=api_key, provider=provider)
            intent_llm = get_model(model_name=model_name, api_key=api_key, provider=provider)
            
            # Safety shim
            class SafetyShim:
                dangerous_commands = config.get('safety', {}).get('blocked_commands', ['rm -rf', 'format']) if isinstance(config.get('safety'), dict) else []
            
            agent_config_shim = SimpleNamespace(
                safety=SafetyShim()
            )
            
            # Init Controller
            llms = {'intent': intent_llm, 'reasoning': reasoning_llm}
            controller = Controller(llms, agent_config_shim, ui)
            agent_available = True
            
            # Init Modes
            hacker_mode = HackerMode(controller, ui, config)
            forge_mode = ForgeMode(controller, ui)
            
    except Exception as e:
        ui.print_error(f"LLM Setup Error: {e}")
        agent_available = False

    history = []

    # 7. Main Loop
    # Status bar callback
    def get_status_html():
        # Update metrics (approximations)
        status_bar.update(
            tokens_used=len(str(history)) // 4,
            context_used=len(history),
            phase="IDLE" if agent_available else "OFFLINE",
            model=model_name
        )
        return status_bar.get_toolbar_content(mode)
    
    while cli_app.running:
        try:
            # Prompt text
            prompt_text = "[!] You: " if mode.lower() == 'hacker' else "[+] You: "
            
            # Get input with status bar
            # Using correct method name: get_input_with_status
            user_input = ui.get_input_with_status(prompt_text, get_status_html).strip()
            
            if not user_input:
                continue
            
            # 1. Try Command Handler
            if user_input.startswith('/'):
                if user_input.startswith('/mode'):
                    # Handle mode switch
                    parts = user_input.split()
                    if len(parts) > 1:
                        new_mode = parts[1].lower()
                        if new_mode in ['normal', 'hacker']:
                            mode = new_mode
                            
                            # Save default mode to config
                            if isinstance(config.get('modes'), dict):
                                config['modes']['default'] = mode
                                config_mgr.save_config()
                                ui.print_success(f"Mode saved as default: {mode}")
                            
                            # Clean switch
                            os.system('cls' if os.name == 'nt' else 'clear')
                            ui.show_banner(mode)
                        else:
                            ui.print_error("Invalid mode. Use: normal or hacker")
                    else:
                        ui.print_info(f"Current mode: {mode}")
                    continue
                    
                if cmd_handler.handle(user_input):
                    continue
            
            # 2. Check keywords
            if user_input.lower() in ['exit', 'quit']:
                cli_app.running = False
                continue
            
            # File Expansion Logic (@file)
            expanded_input = user_input
            if '@' in user_input:
                import re
                # Extract potential file paths using regex
                matches = re.finditer(r'@([a-zA-Z0-9_\-\./\\]+)', user_input)
                
                files_processed = set()
                
                for match in matches:
                    filepath = match.group(1)
                    if filepath in files_processed:
                        continue
                    files_processed.add(filepath)
                    
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            expanded_input += f"\n\n[FILE CONTEXT: {filepath}]\n{content}\n[END FILE]\n"
                            ui.print_info(f"Loaded file: {filepath}")
                        except Exception as e:
                            # ui.print_error(f"Error reading {filepath}: {e}")
                            pass
            
            # 3. Pass to Agent
            if agent_available and controller:
                try:
                    if mode.lower() == 'hacker':
                         # HACKER MODE: Unified Session
                         hacker_mode.chat(expanded_input)
                    else:
                         # NORMAL MODE: Simple Chat
                         
                         response = controller.reasoning_llm.generate(expanded_input, history)
                         
                         history.append({"role": "user", "content": expanded_input})
                         history.append({"role": "assistant", "content": response})
                         
                         # Typing effect output
                         ui.type_text(response)
                        
                except Exception as e:
                    ui.print_error(f"Agent Error: {e}")
            else:
                if not user_input.startswith('/'):
                    ui.print_warning("AI not initialized. Configure API key in /settings")
                
        except KeyboardInterrupt:
            if ui.confirm("\nExit BugPilot?"):
                cli_app.running = False
        except Exception as e:
            ui.print_error(f"Runtime Error: {e}")

    ui.console.print("\n[cyan]Goodbye![/cyan]")

if __name__ == "__main__":
    main()
