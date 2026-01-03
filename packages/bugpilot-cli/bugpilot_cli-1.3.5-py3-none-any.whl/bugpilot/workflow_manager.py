"""
Workflow System for BugPilot CLI
Pre-defined pentesting workflows for common scenarios
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    name: str
    description: str
    command_template: str
    expected_output: str
    on_success: Optional[str] = None
    on_failure: Optional[str] = None


class Workflow:
    """Pentesting workflow definition"""
    
    def __init__(self, name: str, description: str, steps: List[WorkflowStep]):
        self.name = name
        self.description = description
        self.steps = steps
        self.current_step = 0
    
    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get next step in workflow"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        return None
    
    def reset(self):
        """Reset workflow to beginning"""
        self.current_step = 0


class WorkflowManager:
    """Manages pentesting workflows"""
    
    def __init__(self):
        self.workflows = self._load_builtin_workflows()
        self.active_workflow = None
    
    def _load_builtin_workflows(self) -> Dict[str, Workflow]:
        """Load built-in pentesting workflows"""
        return {
            "web_recon": Workflow(
                name="Web Reconnaissance",
                description="Complete web application reconnaissance",
                steps=[
                    WorkflowStep(
                        "DNS Lookup",
                        "Resolve domain to IP address",
                        "nslookup {target}",
                        "IP address"
                    ),
                    WorkflowStep(
                        "Port Scan",
                        "Scan for open ports",
                        "nmap -p- {target}",
                        "Open ports list"
                    ),
                    WorkflowStep(
                        "Service Detection",
                        "Identify services on open ports",
                        "nmap -sV -p {ports} {target}",
                        "Service versions"
                    ),
                    WorkflowStep(
                        "Web Server Scan",
                        "Scan web server for vulnerabilities",
                        "nikto -h {target}",
                        "Vulnerability list"
                    ),
                    WorkflowStep(
                        "Directory Enumeration",
                        "Enumerate directories",
                        "dirb http://{target}",
                        "Directory list"
                    )
                ]
            ),
            
            "sql_injection_test": Workflow(
                name="SQL Injection Testing",
                description="Comprehensive SQL injection testing",
                steps=[
                    WorkflowStep(
                        "Identify Forms",
                        "Find input forms",
                        "curl -s {target} | grep -i form",
                        "Form elements"
                    ),
                    WorkflowStep(
                        "Basic SQLi Test",
                        "Test for basic SQL injection",
                        "sqlmap -u '{target}' --batch --level=1",
                        "Injection points"
                    ),
                    WorkflowStep(
                        "Deep SQLi Test",
                        "Deep SQL injection testing",
                        "sqlmap -u '{target}' --batch --level=5 --risk=3",
                        "Detailed vulnerabilities"
                    ),
                    WorkflowStep(
                        "Database Enumeration",
                        "Enumerate databases if vulnerable",
                        "sqlmap -u '{target}' --dbs --batch",
                        "Database list"
                    )
                ]
            ),
            
            "xss_test": Workflow(
                name="XSS Testing",
                description="Cross-Site Scripting vulnerability testing",
                steps=[
                    WorkflowStep(
                        "Input Discovery",
                        "Find all input points",
                        "curl -s {target} | grep -i 'input\\|textarea'",
                        "Input fields"
                    ),
                    WorkflowStep(
                        "Reflected XSS Test",
                        "Test for reflected XSS",
                        "curl '{target}?param=<script>alert(1)</script>'",
                        "XSS reflection"
                    ),
                    WorkflowStep(
                        "Stored XSS Test",
                        "Test for stored XSS",
                        "# Manual: Submit <script>alert(1)</script> in forms",
                        "Stored XSS confirmation"
                    )
                ]
            ),
            
            "full_pentest": Workflow(
                name="Full Penetration Test",
                description="Complete penetration testing workflow",
                steps=[
                    WorkflowStep("Reconnaissance", "Gather information", "whois {target}", "Domain info"),
                    WorkflowStep("DNS Enumeration", "Enumerate DNS", "nslookup {target}", "DNS records"),
                    WorkflowStep("Port Scanning", "Scan all ports", "nmap -p- {target}", "Open ports"),
                    WorkflowStep("Service Detection", "Detect services", "nmap -sV {target}", "Services"),
                    WorkflowStep("Vulnerability Scan", "Scan for vulns", "nikto -h {target}", "Vulnerabilities"),
                    WorkflowStep("Directory Bruteforce", "Find directories", "dirb http://{target}", "Directories"),
                    WorkflowStep("SQL Injection", "Test SQLi", "sqlmap -u {target} --batch", "SQLi results"),
                    WorkflowStep("XSS Testing", "Test XSS", "# Test XSS payloads", "XSS results"),
                    WorkflowStep("SSL/TLS Check", "Check SSL", "sslscan {target}", "SSL config")
                ]
            ),
            
            "network_scan": Workflow(
                name="Network Scanning",
                description="Network discovery and scanning",
                steps=[
                    WorkflowStep("Ping Sweep", "Discover hosts", "nmap -sn {target}", "Live hosts"),
                    WorkflowStep("Port Scan", "Scan ports", "nmap -p- {target}", "Open ports"),
                    WorkflowStep("OS Detection", "Detect OS", "nmap -O {target}", "Operating system"),
                    WorkflowStep("Service Scan", "Scan services", "nmap -sV {target}", "Services")
                ]
            ),
            
            "api_test": Workflow(
                name="API Security Testing",
                description="Test API endpoints for vulnerabilities",
                steps=[
                    WorkflowStep("Endpoint Discovery", "Find API endpoints", "curl -s {target}/api", "Endpoints"),
                    WorkflowStep("Authentication Test", "Test auth", "curl -X POST {target}/api/login", "Auth status"),
                    WorkflowStep("Authorization Test", "Test authz", "curl -H 'Auth: invalid' {target}/api", "Authz status"),
                    WorkflowStep("Input Validation", "Test inputs", "curl -d 'id=1 OR 1=1' {target}/api", "Validation")
                ]
            )
        }
    
    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get workflow by name"""
        return self.workflows.get(name)
    
    def list_workflows(self) -> List[Dict[str, str]]:
        """List all available workflows"""
        return [
            {
                "name": wf.name,
                "description": wf.description,
                "steps": len(wf.steps)
            }
            for wf in self.workflows.values()
        ]
    
    def start_workflow(self, name: str) -> bool:
        """Start a workflow"""
        workflow = self.get_workflow(name)
        if workflow:
            workflow.reset()
            self.active_workflow = workflow
            return True
        return False
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get current step in active workflow"""
        if self.active_workflow:
            return self.active_workflow.get_next_step()
        return None
    
    def stop_workflow(self):
        """Stop current workflow"""
        self.active_workflow = None
