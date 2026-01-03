"""
CLI Helper Functions for BugPilot
"""

def format_final_report(report: dict) -> str:
    """
    Format the final autonomous session report
    
    Args:
        report: Dictionary containing session results
        
    Returns:
        Formatted string report
    """
    findings_count = len(report.get('findings', {}))
    actions_count = report.get('actions_taken', 0)
    
    formatted = f"""**Objective:** {report['objective']}

**Session Statistics:**
- Iterations: {report['iterations']}
- Actions Taken: {actions_count}
- Findings Discovered: {findings_count}
- Status: {"[+] Success" if report['success'] else "[!] Incomplete"}

**Key Findings:**"""
    
    if findings_count > 0:
        for iteration, finding_data in report['findings'].items():
            formatted += f"\n\n**{iteration.replace('_', ' ').title()}:**"
            for finding in finding_data.get('key_findings', []):
                formatted += f"\n- {finding}"
    else:
        formatted += "\n- No significant findings"
    
    formatted += "\n\n**Executed Actions:**"
    for action in report.get('executed_actions', [])[-5:]:  # Last 5
        status = "[+]" if action['success'] else "[-]"
        formatted += f"\n{status} {action['command']}"
    
    return formatted
