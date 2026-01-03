"""
Logic Engine - The 'Cyber Brain' of BugPilot v1.6.0
Provides automated reasoning and attack strategies for intelligent bug finding.
"""

import re
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs

class LogicEngine:
    """
    Implements hacker logic for automated reasoning.
    Analyzes targets to identify specific attack surfaces and vulnerabilities.
    """

    def __init__(self):
        # Heuristics for parameter analysis
        self.param_signatures = {
            'sqli': ['id', 'user', 'user_id', 'cat', 'category', 'view', 'item', 'query', 's'],
            'xss':  ['q', 'query', 'search', 'keyword', 'name', 'msg', 'message', 'comment'],
            'lfi':  ['file', 'page', 'path', 'doc', 'document', 'folder', 'root', 'include'],
            'ssrf': ['url', 'uri', 'link', 'continue', 'next', 'dest', 'host', 'port'],
            'rce':  ['cmd', 'exec', 'command', 'ping', 'query', 'code'],
            'idor': ['id', 'user_id', 'profile_id', 'order_id', 'account', 'number']
        }
        
        # Intelligent Payloads (Lightweight checks before heavy tools)
        self.probe_payloads = {
            'sqli': ["'", '"', "1' OR '1'='1", "1\" OR \"1\"=\"1"],
            'xss':  ['<script>alert(1)</script>', '"><img src=x onerror=alert(1)>'],
            'lfi':  ['../../../../etc/passwd', '..\\..\\..\\..\\windows\\win.ini'],
            'ssti': ['{{7*7}}', '${7*7}'],
        }

    def analyze_target_surface(self, url: str) -> Dict[str, Any]:
        """
        Intelligently analyzes a URL to determine the most likely vulnerabilities.
        Returns a prioritized 'Attack Plan'.
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        path = parsed.path
        
        analysis = {
            "target": url,
            "has_params": bool(params),
            "interesting_params": [],
            "suggested_attacks": [],
            "risk_score": 0
        }

        # 1. Parameter Analysis (The "Brain")
        for param in params.keys():
            param_lower = param.lower()
            detected_types = []
            
            for vuln_type, signatures in self.param_signatures.items():
                if any(sig in param_lower for sig in signatures):
                    detected_types.append(vuln_type)
            
            if detected_types:
                analysis["interesting_params"].append({
                    "param": param,
                    "suspected_vulns": detected_types
                })
                # Intelligent scoring
                analysis["risk_score"] += len(detected_types) * 10
                
                # Formulate strategy
                for vuln in detected_types:
                    strategy = self._get_attack_strategy(vuln, param)
                    if strategy not in analysis["suggested_attacks"]:
                        analysis["suggested_attacks"].append(strategy)

        # 2. Path Analysis
        if '.php' in path: 
            analysis["suggested_attacks"].append("Check for PHP Info disclosure/config files")
        if '/wp-' in path:
            analysis["suggested_attacks"].append("WordPress detected: Enumerate Plugins/Users")
        if '/api/' in path:
            analysis["suggested_attacks"].append("API Endpoint: Check Broken Object Level Auth (IDOR)")

        # 3. Prioritization
        # If no params, suggest fuzzing
        if not params:
            analysis["suggested_attacks"].append("No parameters visible: Perform Fuzzing to find hidden parameters")

        return analysis

    def _get_attack_strategy(self, vuln_type: str, param: str) -> str:
        """Returns a high-level strategy description for the AI agent"""
        strategies = {
            'sqli': f"TEST SQL INJECTION on parameter '{param}'. Use 'sqlmap' or try inserting single quotes.",
            'xss':  f"TEST REFLECTED XSS on parameter '{param}'. Inject basic script tags.",
            'lfi':  f"TEST PATH TRAVERSAL on parameter '{param}'. Try loading system files (e.g., /etc/passwd).",
            'ssrf': f"TEST SSRF on parameter '{param}'. Try making the server query an external logger.",
            'rce':  f"TEST COMMAND INJECTION on parameter '{param}'. Try injecting system commands (`id`, `whoami`).",
            'idor': f"TEST IDOR on parameter '{param}'. Try changing the ID value to access other users' data."
        }
        return strategies.get(vuln_type, f"Fuzz parameter '{param}' for anomalies.")

    def generate_intelligent_thought(self, url: str) -> str:
        """
        Generates a human-like "Chain of Thought" for the AI to reason about the target.
        """
        analysis = self.analyze_target_surface(url)
        
        thought = f"Analyze URL: {url}\n"
        if analysis["interesting_params"]:
            thought += f"  → Found interesting parameters: {[p['param'] for p in analysis['interesting_params']]}\n"
            thought += f"  → These parameters match signatures for: {[p['suspected_vulns'] for p in analysis['interesting_params']]}\n"
            thought += "  → HIGH INTELLIGENCE STRATEGY:\n"
            for attack in analysis["suggested_attacks"]:
                thought += f"    * {attack}\n"
        else:
            thought += "  → No visible parameters. Strategy: BRUTE FORCE discovery and Technology Detection.\n"
            
        return thought

    def get_next_intelligent_move(self, history: List[Dict]) -> str:
        """
        Decides the next move based on previous failures/successes.
        Prevents 'dumb' looping.
        """
        # (This would be integrated into the main loop to provide hints)
        if not history:
            return "Start with Reconnaissance."
            
        last_action = history[-1]
        
        # If last action loop nmap and found nothing
        if 'nmap' in last_action.get('command', '') and '0 hosts up' in last_action.get('output', ''):
             return "Host seems down. Check if I can ping it, or stop."

        return "Continue with plan."
