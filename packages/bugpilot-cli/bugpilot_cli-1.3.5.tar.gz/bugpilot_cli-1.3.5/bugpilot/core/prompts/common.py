"""Common Prompt Definitions"""

DEVELOPER_INFO = """
Developer: LAKSHMIKANTHAN K (letchupkt)
BugPilot CLI - AI-Powered Penetration Testing Tool
"""

def get_os_context(os_info: dict) -> str:
    """Generate OS-specific context for AI"""
    os_info_dict = os_info if isinstance(os_info, dict) else {}
    os_name = os_info_dict.get('os_name', 'Unknown')
    shell = os_info_dict.get('shell', 'Unknown')
    platform = os_info_dict.get('platform', 'Unknown')
    
    os_context = f"""
## SYSTEM ENVIRONMENT:
**Operating System:** {os_name}
**Shell:** {shell}
**Platform:** {platform}
"""
    
    if os_name == 'Windows':
        os_context += """
**IMPORTANT - Windows Commands:**
- Use PowerShell syntax (Get-*, Test-*, etc.)
- Network scan: `Test-Connection` or `nmap` (if installed)
- DNS: `Resolve-DnsName` or `nslookup`
"""
    elif os_info_dict.get('is_termux'):
        os_context += """
**IMPORTANT - Termux (Android) Environment:**
- Use standard Linux commands
- Tools: nmap, nikto, sqlmap (install via `pkg install`)
"""
    else:  # Linux/macOS
        os_context += """
**IMPORTANT - Linux/Unix Commands:**
- Use bash/sh syntax
- Network: `ping`, `nmap`, `nslookup`
"""
    
    return os_context
