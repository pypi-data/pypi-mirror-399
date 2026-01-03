"""
CVE and Security Knowledge Tools
Free APIs for CVE lookup and OWASP Top 10 information
"""

import requests
from typing import Dict, List, Optional
import json

class CVETools:
    """Tools for CVE information retrieval"""
    
    def __init__(self):
        self.cve_api = "https://cvedb.shodan.io/cve/"
        self.circl_api = "https://cve.circl.lu/api/"
        
    def search_cve(self, cve_id: str) -> Optional[Dict]:
        """
        Search for a specific CVE by ID
        
        Args:
            cve_id: CVE ID (e.g., CVE-2021-44228)
            
        Returns:
            Dict with CVE details or None
        """
        try:
            # Try Shodan CVE Database first
            response = requests.get(f"{self.cve_api}{cve_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            
            # Fallback to CIRCL
            response = requests.get(f"{self.circl_api}cve/{cve_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            print(f"Error fetching CVE: {e}")
        
        return None
    
    def search_product_cve(self, product: str, version: str = None) -> List[Dict]:
        """
        Search for CVEs related to a product/service
        
        Args:
            product: Product name (e.g., "apache", "nginx")
            version: Optional version number
            
        Returns:
            List of CVEs
        """
        try:
            # Use CIRCL API for product search
            search_term = f"{product} {version}" if version else product
            response = requests.get(
                f"{self.circl_api}search/{search_term}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])[:10]  # Limit to 10 results
                
        except Exception as e:
            print(f"Error searching product CVEs: {e}")
        
        return []
    
    def get_recent_cves(self, limit: int = 10) -> List[Dict]:
        """
        Get recent CVEs
        
        Args:
            limit: Number of recent CVEs to fetch
            
        Returns:
            List of recent CVEs
        """
        try:
            response = requests.get(
                f"{self.circl_api}last",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data[:limit]
                
        except Exception as e:
            print(f"Error fetching recent CVEs: {e}")
        
        return []
    
    def get_cve_summary(self, cve_id: str) -> str:
        """
        Get a formatted summary of a CVE
        
        Args:
            cve_id: CVE ID
            
        Returns:
            Formatted string with CVE details
        """
        cve_data = self.search_cve(cve_id)
        
        if not cve_data:
            return f"CVE {cve_id} not found"
        
        summary = f"""
CVE ID: {cve_id}
Summary: {cve_data.get('summary', 'N/A')}
CVSS Score: {cve_data.get('cvss', 'N/A')}
Published: {cve_data.get('Published', 'N/A')}
Modified: {cve_data.get('Modified', 'N/A')}

References:
"""
        
        refs = cve_data.get('references', [])
        for ref in refs[:5]:  # Limit to 5 references
            summary += f"  - {ref}\n"
        
        return summary


class OWASPTools:
    """Tools for OWASP Top 10 information"""
    
    def __init__(self):
        # OWASP Top 10 2021 data
        self.owasp_top10 = {
            "A01:2021": {
                "name": "Broken Access Control",
                "description": "Restrictions on what authenticated users are allowed to do are often not properly enforced.",
                "examples": [
                    "Violation of principle of least privilege",
                    "Bypassing access control checks",
                    "Insecure direct object references (IDOR)"
                ],
                "mitigation": [
                    "Deny by default",
                    "Implement access control mechanisms once and re-use",
                    "Log access control failures"
                ]
            },
            "A02:2021": {
                "name": "Cryptographic Failures",
                "description": "Failures related to cryptography which often leads to sensitive data exposure.",
                "examples": [
                    "Transmitting data in clear text (HTTP, FTP, SMTP)",
                    "Using old or weak cryptographic algorithms",
                    "Missing encryption of sensitive data"
                ],
                "mitigation": [
                    "Encrypt all sensitive data at rest and in transit",
                    "Use strong encryption algorithms",
                    "Disable caching for sensitive data"
                ]
            },
            "A03:2021": {
                "name": "Injection",
                "description": "User-supplied data is not validated, filtered, or sanitized by the application.",
                "examples": [
                    "SQL Injection",
                    "NoSQL Injection",
                    "OS Command Injection",
                    "LDAP Injection"
                ],
                "mitigation": [
                    "Use parameterized queries",
                    "Input validation",
                    "Use ORM frameworks"
                ]
            },
            "A04:2021": {
                "name": "Insecure Design",
                "description": "Missing or ineffective control design.",
                "examples": [
                    "Lack of threat modeling",
                    "Insecure design patterns",
                    "Missing security requirements"
                ],
                "mitigation": [
                    "Establish secure development lifecycle",
                    "Use threat modeling",
                    "Write security unit tests"
                ]
            },
            "A05:2021": {
                "name": "Security Misconfiguration",
                "description": "Missing appropriate security hardening or improperly configured permissions.",
                "examples": [
                    "Default credentials",
                    "Unnecessary features enabled",
                    "Error messages revealing sensitive information"
                ],
                "mitigation": [
                    "Minimal platform without unnecessary features",
                    "Automated deployment process",
                    "Review and update configurations"
                ]
            },
            "A06:2021": {
                "name": "Vulnerable and Outdated Components",
                "description": "Using components with known vulnerabilities.",
                "examples": [
                    "Outdated libraries",
                    "Unsupported software versions",
                    "Not scanning for vulnerabilities regularly"
                ],
                "mitigation": [
                    "Remove unused dependencies",
                    "Continuously inventory versions",
                    "Use software composition analysis tools"
                ]
            },
            "A07:2021": {
                "name": "Identification and Authentication Failures",
                "description": "Confirmation of user's identity, authentication, and session management is critical.",
                "examples": [
                    "Weak passwords",
                    "Credential stuffing",
                    "Missing or ineffective multi-factor authentication"
                ],
                "mitigation": [
                    "Implement multi-factor authentication",
                    "Use strong session management",
                    "Limit failed login attempts"
                ]
            },
            "A08:2021": {
                "name": "Software and Data Integrity Failures",
                "description": "Code and infrastructure that does not protect against integrity violations.",
                "examples": [
                    "Insecure CI/CD pipeline",
                    "Auto-update without verification",
                    "Insecure deserialization"
                ],
                "mitigation": [
                    "Use digital signatures",
                    "Verify integrity of libraries",
                    "Use security review process"
                ]
            },
            "A09:2021": {
                "name": "Security Logging and Monitoring Failures",
                "description": "Insufficient logging and monitoring, coupled with missing or ineffective integration with incident response.",
                "examples": [
                    "Not logging authentication failures",
                    "Missing alerts for suspicious activities",
                    "Logs not being monitored"
                ],
                "mitigation": [
                    "Log all authentication and access control failures",
                    "Ensure logs are in a format for analysis",
                    "Establish effective monitoring and alerting"
                ]
            },
            "A10:2021": {
                "name": "Server-Side Request Forgery (SSRF)",
                "description": "SSRF flaws occur when a web application fetches a remote resource without validating the user-supplied URL.",
                "examples": [
                    "Access to internal services",
                    "Port scanning internal network",
                    "Reading local files"
                ],
                "mitigation": [
                    "Whitelist allowed URLs",
                    "Disable unused URL schemas",
                    "Don't send raw responses to clients"
                ]
            }
        }
    
    def get_owasp_item(self, item_id: str) -> Optional[Dict]:
        """
        Get details about a specific OWASP Top 10 item
        
        Args:
            item_id: OWASP ID (e.g., "A01:2021" or just "A01")
            
        Returns:
            Dict with OWASP details or None
        """
        # Handle both "A01" and "A01:2021" formats
        if ":" not in item_id:
            item_id = f"{item_id}:2021"
        
        return self.owasp_top10.get(item_id)
    
    def get_all_owasp_top10(self) -> Dict:
        """Get all OWASP Top 10 2021 items"""
        return self.owasp_top10
    
    def search_owasp(self, keyword: str) -> List[Dict]:
        """
        Search OWASP Top 10 by keyword
        
        Args:
            keyword: Search term
            
        Returns:
            List of matching OWASP items
        """
        results = []
        keyword_lower = keyword.lower()
        
        for item_id, item_data in self.owasp_top10.items():
            if (keyword_lower in item_data['name'].lower() or 
                keyword_lower in item_data['description'].lower() or
                any(keyword_lower in ex.lower() for ex in item_data['examples'])):
                results.append({
                    'id': item_id,
                    **item_data
                })
        
        return results
    
    def get_owasp_summary(self, item_id: str = None) -> str:
        """
        Get formatted summary of OWASP item(s)
        
        Args:
            item_id: Optional specific OWASP ID, if None returns all
            
        Returns:
            Formatted string with OWASP details
        """
        if item_id:
            item = self.get_owasp_item(item_id)
            if not item:
                return f"OWASP item {item_id} not found"
            
            return f"""
{item_id} - {item['name']}

Description:
{item['description']}

Common Examples:
{chr(10).join(f"  • {ex}" for ex in item['examples'])}

Mitigation:
{chr(10).join(f"  ✓ {mit}" for mit in item['mitigation'])}
"""
        else:
            summary = "OWASP Top 10 2021:\n\n"
            for item_id, item_data in self.owasp_top10.items():
                summary += f"{item_id} - {item_data['name']}\n"
            return summary


# Global instances
cve_tools = CVETools()
owasp_tools = OWASPTools()


def get_cve_info(cve_id: str) -> str:
    """Get CVE information - can be called by AI"""
    return cve_tools.get_cve_summary(cve_id)


def search_cves_for_product(product: str, version: str = None) -> str:
    """Search CVEs for a product - can be called by AI"""
    results = cve_tools.search_product_cve(product, version)
    if not results:
        return f"No CVEs found for {product} {version or ''}"
    
    output = f"CVEs for {product} {version or ''}:\n\n"
    for cve in results[:10]:
        output += f"• {cve.get('id', 'N/A')} - {cve.get('summary', 'N/A')[:100]}...\n"
    
    return output


def get_owasp_info(item_id: str = None) -> str:
    """Get OWASP Top 10 information - can be called by AI"""
    return owasp_tools.get_owasp_summary(item_id)


def search_owasp_vulnerability(keyword: str) -> str:
    """Search OWASP Top 10 by keyword - can be called by AI"""
    results = owasp_tools.search_owasp(keyword)
    if not results:
        return f"No OWASP items found for '{keyword}'"
    
    output = f"OWASP Top 10 results for '{keyword}':\n\n"
    for item in results:
        output += f"{item['id']} - {item['name']}\n{item['description'][:150]}...\n\n"
    
    return output
