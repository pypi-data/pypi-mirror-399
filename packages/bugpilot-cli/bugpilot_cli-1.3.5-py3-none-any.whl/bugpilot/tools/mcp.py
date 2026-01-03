"""
MCP (Model Context Protocol) Integration
Enables enhanced context management and tool usage
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class MCPContext:
    """Manages Model Context Protocol for enhanced AI interactions"""
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or Path.home() / ".bugpilot" / "workspace"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.context_file = self.workspace_dir / "mcp_context.json"
        self.tools_registry = {}
        self.active_sessions = {}
    
    def register_tool(self, name: str, description: str, executor):
        """Register a tool for MCP usage"""
        self.tools_registry[name] = {
            "description": description,
            "executor": executor
        }
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of available tools"""
        return [
            {"name": name, "description": info["description"]}
            for name, info in self.tools_registry.items()
        ]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        if tool_name not in self.tools_registry:
            raise ValueError(f"Tool {tool_name} not found")
        
        executor = self.tools_registry[tool_name]["executor"]
        return executor(**kwargs)
    
    def save_session_context(self, session_id: str, context: Dict[str, Any]):
        """Save session context to file"""
        self.active_sessions[session_id] = context
        
        with open(self.context_file, 'w') as f:
            json.dump(self.active_sessions, f, indent=2)
    
    def load_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session context from file"""
        if self.context_file.exists():
            with open(self.context_file, 'r') as f:
                self.active_sessions = json.load(f)
        
        return self.active_sessions.get(session_id)
    
    def create_context_summary(self, context: List[Dict[str, str]]) -> str:
        """Create a summary of current context"""
        if not context:
            return "No context available"
        
        summary = []
        for i, msg in enumerate(context[-5:], 1):  # Last 5 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:100]  # First 100 chars
            summary.append(f"{i}. {role}: {content}...")
        
        return "\n".join(summary)


# Default tool implementations
def nmap_scan(target: str, flags: str = "-sV") -> str:
    """Execute nmap scan"""
    import subprocess
    try:
        result = subprocess.run(
            ["nmap", flags, target],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except Exception as e:
        return f"Error running nmap: {str(e)}"


def subdomain_enum(domain: str) -> str:
    """Enumerate subdomains"""
    import subprocess
    try:
        result = subprocess.run(
            ["subfinder", "-d", domain, "-silent"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except Exception as e:
        return f"Error running subfinder: {str(e)}"


def nuclei_scan(target: str) -> str:
    """Run nuclei vulnerability scanner"""
    import subprocess
    try:
        result = subprocess.run(
            ["nuclei", "-u", target, "-silent"],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout
    except Exception as e:
        return f"Error running nuclei: {str(e)}"


# Initialize default MCP with tools
def initialize_default_mcp() -> MCPContext:
    """Initialize MCP with default tools"""
    mcp = MCPContext()
    
    mcp.register_tool(
        "nmap_scan",
        "Perform network port scanning with nmap",
        nmap_scan
    )
    
    mcp.register_tool(
        "subdomain_enum",
        "Enumerate subdomains of a target domain",
        subdomain_enum
    )
    
    mcp.register_tool(
        "nuclei_scan",
        "Run nuclei vulnerability scanner on target",
        nuclei_scan
    )
    
    return mcp
