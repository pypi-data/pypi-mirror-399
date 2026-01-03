"""
Dynamic Context Analyzer - BugPilot v1.6.0
Dynamically extracts context and discovers available tools found on the system.
No hardcoded rules. The AI decides how to use this data.
"""

import shutil
import os
from urllib.parse import urlparse, parse_qs
from typing import Dict, List

class DynamicContext:
    """
    Feeds dynamic environment data to the AI.
    1. Discovers what tools are actually installed.
    2. Parses targets to give AI 'senses'.
    """

    def __init__(self):
        self.available_tools = self._discover_tools()

    def _discover_tools(self) -> Dict[str, str]:
        """
        Dynamically checks the OS environment for known hacker tools.
        Returns a map of {tool_name: path}.
        """
        potential_tools = [
            # Scanners
            "nmap", "nikto", "nuclei", "whatweb", "wafw00f",
            # Web
            "sqlmap", "wpscan", "joomscan", "droopescan", "feroxbuster", "gobuster", "ffuf", "dirb",
            # Exploitation
            "hydra", "medusa", "metasploit", "searchsploit", "commix"
        ]
        
        found = {}
        for tool in potential_tools:
            path = shutil.which(tool)
            if path:
                found[tool] = path
        
        return found

    def get_tool_arsenal(self) -> str:
        """Returns a string description of what is actually usable right now."""
        if not self.available_tools:
            return "Basic System Tools (curl, ping, wget)"
            
        return ", ".join(self.available_tools.keys())

    def parse_target(self, url: str) -> str:
        """
        Parses a target to give the AI raw data for reasoning.
        Does NOT make decisions. Just provides the 'sight'.
        """
        if not url: return "No target."
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        info = []
        info.append(f"Domain: {parsed.netloc}")
        info.append(f"Path: {parsed.path}")
        
        if params:
            param_list = list(params.keys())
            info.append(f"Parameters Detected: {', '.join(param_list)}")
            info.append(f"  -> AI Hint: Analyzes these parameters for potential injection points.")
        else:
            info.append("No URL parameters visible.")
            
        return "\n".join(info)
