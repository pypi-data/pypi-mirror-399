"""
Dynamic Tool Manager - Auto-install and manage pentesting tools
"""

import subprocess
import platform
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class ToolManager:
    """Manages installation and verification of pentesting tools"""
    
    # Comprehensive tool database
    TOOLS = {
        # Network Scanning
        "nmap": {
            "category": "network_scan",
            "description": "Network exploration and security auditing",
            "install": {
                "linux": "sudo apt-get install -y nmap",
                "termux": "pkg install -y nmap",
                "darwin": "brew install nmap",
                "windows": "choco install nmap -y"
            }
        },
        "masscan": {
            "category": "network_scan",
            "description": "Fast TCP port scanner",
            "install": {
                "linux": "sudo apt-get install -y masscan",
                "termux": "pkg install -y masscan",
                "darwin": "brew install masscan",
                "windows": "choco install masscan -y"
            }
        },
        
        # Web Scanning
        "nikto": {
            "category": "web_scan",
            "description": "Web server vulnerability scanner",
            "install": {
                "linux": "sudo apt-get install -y nikto",
                "termux": "pkg install -y nikto",
                "darwin": "brew install nikto",
                "windows": "choco install nikto -y"
            }
        },
        "wpscan": {
            "category": "web_scan",
            "description": "WordPress security scanner",
            "install": {
                "linux": "sudo apt-get install -y wpscan",
                "termux": "gem install wpscan",
                "darwin": "brew install wpscan",
                "windows": "gem install wpscan"
            }
        },
        
        # Fuzzing & Directory Discovery
        "ffuf": {
            "category": "fuzzing",
            "description": "Fast web fuzzer",
            "install": {
                "linux": "go install github.com/ffuf/ffuf@latest",
                "termux": "go install github.com/ffuf/ffuf@latest",
                "darwin": "brew install ffuf",
                "windows": "go install github.com/ffuf/ffuf@latest"
            }
        },
        "gobuster": {
            "category": "fuzzing",
            "description": "Directory/file brute forcing",
            "install": {
                "linux": "go install github.com/OJ/gobuster/v3@latest",
                "termux": "go install github.com/OJ/gobuster/v3@latest",
                "darwin": "brew install gobuster",
                "windows": "go install github.com/OJ/gobuster/v3@latest"
            }
        },
        
        # Vulnerability Scanning
        "nuclei": {
            "category": "vuln_scan",
            "description": "Vulnerability scanner based on templates",
            "install": {
                "linux": "go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest",
                "termux": "go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest",
                "darwin": "brew install nuclei",
                "windows": "go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest"
            }
        },
        
        # Subdomain Enumeration
        "subfinder": {
            "category": "recon",
            "description": "Subdomain discovery tool",
            "install": {
                "linux": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
                "termux": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
                "darwin": "brew install subfinder",
                "windows": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
            }
        },
        "amass": {
            "category": "recon",
            "description": "In-depth subdomain enumeration",
            "install": {
                "linux": "go install -v github.com/OWASP/Amass/v3/...@master",
                "termux": "go install -v github.com/OWASP/Amass/v3/...@master",
                "darwin": "brew install amass",
                "windows": "go install -v github.com/OWASP/Amass/v3/...@master"
            }
        },
        
        # HTTP Tools
        "httpx": {
            "category": "recon",
            "description": "Fast HTTP toolkit",
            "install": {
                "linux": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
                "termux": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
                "darwin": "brew install httpx",
                "windows": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
            }
        },
        
        # SQL Injection
        "sqlmap": {
            "category": "exploitation",
            "description": "Automatic SQL injection tool",
            "install": {
                "linux": "sudo apt-get install -y sqlmap",
                "termux": "pkg install -y sqlmap",
                "darwin": "brew install sqlmap",
                "windows": "pip install sqlmap"
            }
        },
        
        # DNS Tools
        "dnsx": {
            "category": "recon",
            "description": "Fast DNS toolkit",
            "install": {
                "linux": "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
                "termux": "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
                "darwin": "brew install dnsx",
                "windows": "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
            }
        },
        
        # Network Tools
        "netcat": {
            "category": "network",
            "description": "Network utility for reading/writing network connections",
            "install": {
                "linux": "sudo apt-get install -y netcat",
                "termux": "pkg install -y netcat",
                "darwin": "brew install netcat",
                "windows": "choco install netcat -y"
            }
        },
        
        # Git Tools
        "git": {
            "category": "utility",
            "description": "Version control system",
            "install": {
                "linux": "sudo apt-get install -y git",
                "termux": "pkg install -y git",
                "darwin": "brew install git",
                "windows": "choco install git -y"
            }
        },
        
        # Python
        "python3": {
            "category": "utility",
            "description": "Python 3 interpreter",
            "install": {
                "linux": "sudo apt-get install -y python3 python3-pip",
                "termux": "pkg install -y python",
                "darwin": "brew install python3",
                "windows": "choco install python -y"
            }
        },
        
        # Go (for installing Go tools)
        "go": {
            "category": "utility",
            "description": "Go programming language",
            "install": {
                "linux": "sudo apt-get install -y golang",
                "termux": "pkg install -y golang",
                "darwin": "brew install go",
                "windows": "choco install golang -y"
            }
        }
    }
    
    def __init__(self):
        self.os_type = platform.system().lower()
        if self.os_type == "linux" and "TERMUX_VERSION" in os.environ:
            self.os_type = "termux"
        
        self.installed_tools = {}
        self.check_all_tools()
    
    def check_tool_installed(self, tool_name: str) -> bool:
        """Check if a tool is installed"""
        try:
            if self.os_type == "windows":
                result = subprocess.run(
                    ["where", tool_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ["which", tool_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            return result.returncode == 0
        except Exception:
            return False
    
    def check_all_tools(self):
        """Check installation status of all tools"""
        for tool_name in self.TOOLS.keys():
            self.installed_tools[tool_name] = self.check_tool_installed(tool_name)
    
    def get_tool_status(self) -> Dict[str, Dict]:
        """Get status of all tools organized by category"""
        status = {}
        
        for tool_name, tool_info in self.TOOLS.items():
            category = tool_info["category"]
            if category not in status:
                status[category] = []
            
            status[category].append({
                "name": tool_name,
                "installed": self.installed_tools.get(tool_name, False),
                "description": tool_info["description"]
            })
        
        return status
    
    def install_tool(self, tool_name: str) -> Tuple[bool, str]:
        """Install a specific tool"""
        if tool_name not in self.TOOLS:
            return False, f"Unknown tool: {tool_name}"
        
        tool_info = self.TOOLS[tool_name]
        
        if self.os_type not in tool_info["install"]:
            return False, f"Installation not supported on {self.os_type}"
        
        install_cmd = tool_info["install"][self.os_type]
        
        try:
            # Show installation command
            output = f"Installing {tool_name} using: {install_cmd}\n"
            
            # Execute installation
            result = subprocess.run(
                install_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Verify installation
                if self.check_tool_installed(tool_name):
                    self.installed_tools[tool_name] = True
                    return True, f"Successfully installed {tool_name}"
                else:
                    return False, f"Installation completed but {tool_name} not found in PATH"
            else:
                return False, f"Installation failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"Installation timed out after 5 minutes"
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def auto_install_missing(self, required_tools: List[str]) -> Dict[str, bool]:
        """Automatically install missing required tools"""
        results = {}
        
        for tool in required_tools:
            if tool in self.TOOLS and not self.installed_tools.get(tool, False):
                success, message = self.install_tool(tool)
                results[tool] = success
            else:
                results[tool] = True  # Already installed
        
        return results
    
    def get_missing_tools(self) -> List[str]:
        """Get list of missing tools"""
        return [
            tool for tool, installed in self.installed_tools.items()
            if not installed
        ]
    
    def get_installed_tools(self) -> List[str]:
        """Get list of installed tools"""
        return [
            tool for tool, installed in self.installed_tools.items()
            if installed
        ]
    
    def suggest_tools_for_task(self, task: str) -> List[str]:
        """Suggest tools based on task description"""
        task_lower = task.lower()
        suggestions = []
        
        # Network scanning
        if any(word in task_lower for word in ['scan', 'port', 'network', 'host']):
            suggestions.extend(['nmap', 'masscan'])
        
        # Web scanning
        if any(word in task_lower for word in ['web', 'http', 'site', 'wordpress']):
            suggestions.extend(['nikto', 'httpx', 'wpscan'])
        
        # Subdomain enumeration
        if any(word in task_lower for word in ['subdomain', 'dns', 'domain']):
            suggestions.extend(['subfinder', 'amass', 'dnsx'])
        
        # Fuzzing
        if any(word in task_lower for word in ['fuzz', 'directory', 'brute']):
            suggestions.extend(['ffuf', 'gobuster'])
        
        # Vulnerability scanning
        if any(word in task_lower for word in ['vulnerability', 'vuln', 'cve']):
            suggestions.append('nuclei')
        
        # SQL injection
        if any(word in task_lower for word in ['sql', 'injection', 'sqli']):
            suggestions.append('sqlmap')
        
        return list(set(suggestions))  # Remove duplicates
