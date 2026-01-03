"""
OS Detection Module
Detects operating system and provides appropriate commands
"""

import os
import platform
import shutil


def detect_os_environment():
    """Detect operating system and environment details"""
    
    os_info = {
        "os_type": os.name,  # 'nt' for Windows, 'posix' for Unix-like
        "os_name": "",
        "platform": platform.system(),
        "shell": "",
        "is_termux": False,
        "is_wsl": False
    }
    
    # Detect specific environment
    if os.name == 'nt':
        os_info['os_name'] = 'Windows'
        os_info['shell'] = 'PowerShell'
    else:
        # Check for Termux
        if os.path.exists('/data/data/com.termux'):
            os_info['os_name'] = 'Termux (Android)'
            os_info['is_termux'] = True
            os_info['shell'] = 'bash/sh'
        # Check for WSL  
        elif 'microsoft' in platform.uname().release.lower():
            os_info['os_name'] = 'WSL (Linux on Windows)'
            os_info['is_wsl'] = True
            os_info['shell'] = 'bash'
        # Regular Linux
        elif platform.system() == 'Linux':
            os_info['os_name'] = 'Linux'
            os_info['shell'] = 'bash'
        # macOS
        elif platform.system() == 'Darwin':
            os_info['os_name'] = 'macOS'
            os_info['shell'] = 'zsh/bash'
        else:
            os_info['os_name'] = 'Unix-like'
            os_info['shell'] = 'sh'
    
    return os_info


def get_os_context_prompt(os_info):
    """Generate OS-specific context for AI prompts"""
    
    os_context = f"""
## SYSTEM ENVIRONMENT:
**Operating System:** {os_info['os_name']}
**Shell:** {os_info['shell']}
**Platform:** {os_info['platform']}

"""
    
    if os_info['os_name'] == 'Windows':
        os_context += """**CRITICAL - Use Windows Commands:**
- Network: `Test-Connection hostname` or `nmap`
- DNS: `Resolve-DnsName` or `nslookup`
- Processes: `Get-Process`
- Services: `Get-Service`
- Web requests: `Invoke-WebRequest`

Example:
```powershell
Test-Connection google.com -Count 4
```
"""
    elif os_info['is_termux']:
        os_context += """**CRITICAL - Termux Environment:**
- Install tools: `pkg install toolname`
- Standard Linux commands available
- Tools: nmap, nikto, sqlmap, curl, wget

Example:
```bash
pkg install nmap
nmap -sV target.com
```
"""
    else:  # Linux/macOS
        os_context += """**CRITICAL - Linux/Unix Commands:**
- Network: `nmap`, `ping`, `nslookup`
- Processes: `ps aux`
- Services: `systemctl` or `service`
- Package manager: `apt`, `yum`, `brew` (macOS)

Example:
```bash
nmap -sV -p 1-1000 target.com
```
"""
    
    return os_context


# Detect OS at module import
OS_INFO = detect_os_environment()
