"""Executor - Runs commands and tools"""

import subprocess
import os
from typing import Dict


class Executor:
    """Executes commands safely"""
    
    def __init__(self, safety_config, timeout=300):
        self.safety = safety_config
        self.timeout = timeout
    
    def execute(self, command: str, timeout: int = None) -> Dict:
        """Execute shell command"""
        
        # Use provided timeout or default
        cmd_timeout = timeout if timeout else self.timeout
        
        # Safety check
        if any(dangerous in command.lower() for dangerous in self.safety.dangerous_commands):
            return {
                'success': False,
                'output': 'Command blocked by safety rules',
                'blocked': True
            }
        
        try:
            if os.name == 'nt':
                result = subprocess.run(['powershell', '-Command', command], 
                                      capture_output=True, text=True, timeout=cmd_timeout)
            else:
                result = subprocess.run(['bash', '-c', command],
                                      capture_output=True, text=True, timeout=cmd_timeout)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {'success': False, 'output': f'Error: {str(e)}'}
