"""Forge Mode - Simple assistant mode"""

from ..agent.controller import Controller


class ForgeMode:
    """Basic AI assistant mode - wraps existing normal mode logic"""
    
    def __init__(self, controller: Controller, ui):
        self.controller = controller
        self.ui = ui
    
    def run(self, user_input: str):
        """Process input in forge mode"""
        
        result = self.controller.process(user_input)
        
        if result['type'] == 'greeting':
            self.ui.print_panel(result['response'], title="[AI] BugPilot", style="success")
        
        elif result['type'] == 'answer':
            # Use existing UI typing effect
            from rich.panel import Panel
            from rich.markdown import Markdown
            self.ui.console.print(Panel(Markdown(result['response']), 
                                       title="[AI] BugPilot", border_style="green"))
        
        elif result['type'] == 'execution':
            # Display execution result
            res = result['result']
            self.ui.console.print(Panel(res['output'][:1000], 
                                       title="[+] Output" if res['success'] else "[-] Failed",
                                       border_style="green" if res['success'] else "red"))
            
            if result.get('analysis'):
                from rich.markdown import Markdown
                self.ui.console.print(Panel(Markdown(result['analysis']),
                                           title="Analysis", border_style="cyan"))
        
        elif result['type'] == 'autonomous':
            self.ui.console.print("[yellow]Complex task detected. Switch to hacker mode for autonomous execution.[/yellow]")
