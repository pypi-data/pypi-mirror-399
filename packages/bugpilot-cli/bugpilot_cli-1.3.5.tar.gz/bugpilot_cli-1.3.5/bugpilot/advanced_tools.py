"""
Advanced Tool Wrapper - Intelligent tool selection and execution
Part of BugPilot v1.4.0 Intelligence Upgrade
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ToolInfo:
    """Information about a pentesting tool"""
    name: str
    category: str
    description: str
    command_template: str
    use_when: List[str]  # Conditions when to use this tool
    dependencies: List[str] = None


class AdvancedToolSelector:
    """Intelligently select tools based on context"""
    
    def __init__(self):
        self.tools = self._define_tools()
        self.used_tools = set()
    
    def _define_tools(self) -> Dict[str, ToolInfo]:
        """Define all available advanced tools"""
        return {
            # Reconnaissance Phase
            "whatweb": ToolInfo(
                name="whatweb",
                category="recon",
                description="Web technology detection",
                command_template="whatweb {url}",
                use_when=["initial_recon", "tech_detection"]
            ),
            "wafw00f": ToolInfo(
                name="wafw00f",
                category="recon",
                description="WAF detection",
                command_template="wafw00f {url}",
                use_when=["waf_detection", "initial_recon"]
            ),
            "nmap_service": ToolInfo(
                name="nmap",
                category="recon",
                description="Service and version detection",
                command_template="nmap -sV -sC {target}",
                use_when=["port_scan", "service_detection"]
            ),
            
            # Vulnerability Scanning Phase
            "nikto": ToolInfo(
                name="nikto",
                category="vuln_scan",
                description="Web vulnerability scanner",
                command_template="nikto -h {url}",
                use_when=["web_scan", "vuln_detection"]
            ),
            "nuclei": ToolInfo(
                name="nuclei",
                category="vuln_scan",
                description="Template-based vulnerability scanner",
                command_template="nuclei -u {url} -t cves/",
                use_when=["cve_scan", "template_based_scan"]
            ),
            "wpscan": ToolInfo(
                name="wpscan",
                category="vuln_scan",
                description="WordPress vulnerability scanner",
                command_template="wpscan --url {url} --enumerate u,p",
                use_when=["wordpress_detected", "cms_scan"]
            ),
            
            # Exploitation Phase
            "sqlmap": ToolInfo(
                name="sqlmap",
                category="exploit",
                description="SQL injection exploitation",
                command_template="sqlmap -u '{url}' --batch --forms",
                use_when=["login_form_found", "sql_injection_suspected", "database_interaction"]
            ),
            "sqlmap_dump": ToolInfo(
                name="sqlmap",
                category="exploit",
                description="SQL injection data extraction",
                command_template="sqlmap -u '{url}' --batch --dump",
                use_when=["sql_injection_confirmed", "data_extraction"]
            ),
            "ffuf": ToolInfo(
                name="ffuf",
                category="exploit",
                description="Directory and file fuzzing",
                command_template="ffuf -u {url}/FUZZ -w /usr/share/wordlists/dirb/common.txt",
                use_when=["directory_brute_force", "file_discovery"]
            ),
            "dirb": ToolInfo(
                name="dirb",
                category="exploit",
                description="Directory brute forcing",
                command_template="dirb {url}",
                use_when=["directory_discovery", "hidden_files"]
            ),
        }
    
    def select_best_tool(self, context: Dict) -> Optional[Tuple[str, ToolInfo]]:
        """
        Intelligently select the best tool based on current context
        
        Args:
            context: Dictionary containing:
                - phase: Current testing phase (recon, scan, exploit)
                - findings: List of previous findings
                - target_info: Info about the target
                - used_tools: Tools already used
        
        Returns:
            Tuple of (command, ToolInfo) or None
        """
        phase = context.get('phase', 'recon')
        findings = context.get('findings', [])
        target_info = context.get('target_info', {})
        
        # Priority scoring system
        tool_scores = {}
        
        for tool_id, tool in self.tools.items():
            score = 0
            
            # Skip if already used (unless it's an exploit tool)
            if tool_id in self.used_tools and tool.category != 'exploit':
                continue
            
            # Phase matching
            if tool.category == phase:
                score += 10
            
            # Context matching
            for condition in tool.use_when:
                # Check if condition matches findings or context
                if self._condition_matches(condition, findings, target_info):
                    score += 5
            
            # WordPress detected? Prioritize wpscan
            if 'wordpress' in str(findings).lower() and tool_id == 'wpscan':
                score += 20
            
            # Login form found? Prioritize sqlmap
            if 'login' in str(findings).lower() or 'form' in str(findings).lower():
                if tool_id in ['sqlmap', 'sqlmap_dump']:
                    score += 15
            
            # If we already did recon, boost exploit tools
            if len(self.used_tools) > 3 and tool.category == 'exploit':
                score += 10
            
            if score > 0:
                tool_scores[tool_id] = score
        
        if not tool_scores:
            return None
        
        # Select highest scoring tool
        best_tool_id = max(tool_scores, key=tool_scores.get)
        best_tool = self.tools[best_tool_id]
        
        # Mark as used
        self.used_tools.add(best_tool_id)
        
        return (best_tool_id, best_tool)
    
    def _condition_matches(self, condition: str, findings: List, target_info: Dict) -> bool:
        """Check if a condition matches current context"""
        condition_lower = condition.lower()
        findings_text = ' '.join(str(f).lower() for f in findings)
        
        # Simple keyword matching
        return condition_lower in findings_text or condition_lower in str(target_info).lower()
    
    def get_recommended_tools(self, phase: str) -> List[ToolInfo]:
        """Get all recommended tools for a specific phase"""
        return [tool for tool in self.tools.values() if tool.category == phase]
    
    def format_command(self, tool: ToolInfo, **kwargs) -> str:
        """Format a tool command with parameters"""
        return tool.command_template.format(**kwargs)
