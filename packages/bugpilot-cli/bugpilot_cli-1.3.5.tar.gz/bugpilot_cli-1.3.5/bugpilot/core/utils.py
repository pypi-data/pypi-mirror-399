"""
Utility functions for BugPilot CLI
"""

import os
import sys
import platform
import subprocess
from typing import Tuple, Optional, List
from pathlib import Path


def get_system_info() -> dict:
    """Get system information"""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "user": os.getenv("USER") or os.getenv("USERNAME"),
    }


def check_tool_installed(tool_name: str) -> bool:
    """Check if a pentesting tool is installed"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["where", tool_name],
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                ["which", tool_name],
                capture_output=True,
                text=True
            )
        return result.returncode == 0
    except Exception:
        return False


def get_installed_tools() -> List[str]:
    """Get list of installed pentesting tools"""
    common_tools = [
        "nmap", "masscan", "nikto", "sqlmap", "burpsuite",
        "metasploit", "ffuf", "gobuster", "subfinder", "amass",
        "nuclei", "httpx", "dnsx", "waybackurls", "gau",
        "aquatone", "photon", "arjun", "wpscan", "dirsearch"
    ]
    
    installed = []
    for tool in common_tools:
        if check_tool_installed(tool):
            installed.append(tool)
    
    return installed


def format_command_output(output: str, max_lines: int = 50) -> str:
    """Format command output for display"""
    lines = output.split('\n')
    
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + f"\n... (truncated {len(lines) - max_lines} lines)"
    
    return output


def create_workspace(workspace_name: str) -> Path:
    """Create a workspace directory for organizing findings"""
    workspace_dir = Path.home() / ".bugpilot" / "workspaces" / workspace_name
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (workspace_dir / "reconnaissance").mkdir(exist_ok=True)
    (workspace_dir / "vulnerabilities").mkdir(exist_ok=True)
    (workspace_dir / "exploits").mkdir(exist_ok=True)
    (workspace_dir / "reports").mkdir(exist_ok=True)
    
    return workspace_dir


def save_finding(workspace: Path, category: str, filename: str, content: str):
    """Save a finding to the workspace"""
    finding_file = workspace / category / filename
    
    with open(finding_file, 'w') as f:
        f.write(content)
    
    return finding_file


def load_wordlist(wordlist_name: str) -> Optional[List[str]]:
    """Load a wordlist file"""
    common_wordlist_locations = [
        f"/usr/share/wordlists/{wordlist_name}",
        f"/usr/share/seclists/{wordlist_name}",
        f"~/.bugpilot/wordlists/{wordlist_name}",
    ]
    
    for location in common_wordlist_locations:
        path = Path(location).expanduser()
        if path.exists():
            with open(path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
    
    return None


def parse_nmap_output(nmap_output: str) -> dict:
    """Parse nmap output into structured data"""
    result = {
        "open_ports": [],
        "services": {},
        "os_detection": None,
    }
    
    # Simple parsing - can be enhanced
    for line in nmap_output.split('\n'):
        if "/tcp" in line or "/udp" in line:
            parts = line.split()
            if len(parts) >= 3:
                port = parts[0]
                service = parts[2] if len(parts) > 2 else "unknown"
                result["open_ports"].append(port)
                result["services"][port] = service
    
    return result


def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text"""
    import re
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def extract_ips_from_text(text: str) -> List[str]:
    """Extract IP addresses from text"""
    import re
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return re.findall(ip_pattern, text)


def extract_domains_from_text(text: str) -> List[str]:
    """Extract domain names from text"""
    import re
    domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
    return re.findall(domain_pattern, text)


def calculate_cvss_score(metrics: dict) -> float:
    """Calculate CVSS score (simplified)"""
    # This is a simplified version
    # Real CVSS calculation is more complex
    base_score = 0.0
    
    impact = metrics.get("impact", "none").lower()
    if impact == "critical":
        base_score += 4.0
    elif impact == "high":
        base_score += 3.0
    elif impact == "medium":
        base_score += 2.0
    elif impact == "low":
        base_score += 1.0
    
    complexity = metrics.get("complexity", "high").lower()
    if complexity == "low":
        base_score += 3.0
    elif complexity == "medium":
        base_score += 2.0
    else:
        base_score += 1.0
    
    return min(base_score, 10.0)


def get_exploit_db_id(cve_id: str) -> Optional[str]:
    """Get Exploit-DB ID for a CVE (placeholder)"""
    # This would normally query Exploit-DB API
    return None


def check_api_key_validity(provider: str, api_key: str) -> bool:
    """Check if an API key is valid"""
    try:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # Try a simple request
            model = genai.GenerativeModel("gemini-pro")
            model.generate_content("test")
            return True
        # Add other providers as needed
    except Exception:
        return False
    
    return False
