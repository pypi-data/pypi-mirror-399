"""Main entry point for refactored BugPilot"""

import os
from bugpilot.core.config.settings import ConfigManager
from bugpilot.core.llm.registry import LLMRegistry
from bugpilot.agent.controller import Controller
from bugpilot.modes.forge import ForgeMode
from bugpilot.modes.hacker import HackerMode


def main():
    """Main entry point"""
    
    # Load configuration
    config_mgr = ConfigManager()
    config = config_mgr.load()
    
    # Get API key
    api_key = config_mgr.get_api_key(config.llm.provider)
    if not api_key:
        print(f"Error: No API key found for {config.llm.provider}")
        print(f"Set {config.llm.provider.upper()}_API_KEY environment variable")
        return
    
    # Update config with API key
    config.llm.api_key = api_key
    
    # Initialize LLMs
    llms = LLMRegistry.create_from_config(config)
    
    # Initialize UI (use existing)
    from bugpilot.core.terminal_ui import TerminalUI
    ui = TerminalUI()
    
    # Create controller
    controller = Controller(llms, config, ui)
    
    # Determine mode
    mode = os.getenv('BUGPILOT_MODE', config.modes.default)
    
    if mode == 'hacker':
        mode_handler = HackerMode(controller, ui, config)
    else:
        mode_handler = ForgeMode(controller, ui)
    
    # Show banner
    ui.show_banner(mode)
    
    # Main loop
    print(f"\n[{mode.upper()} MODE] Type 'exit' to quit\n")
    
    while True:
        try:
            user_input = input(f"\n[!] You: " if mode == "hacker" else "\n[+] You: ").strip()  
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # Settings command
            if user_input.lower() in ['settings', 'config', 'configure']:
                from bugpilot.core.config.editor import SettingsEditor
                editor = SettingsEditor()
                editor.show_main_menu()
                # Reload config
                config = config_mgr.load()
                continue
            
            if not user_input:
                continue
            
            mode_handler.run(user_input)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
