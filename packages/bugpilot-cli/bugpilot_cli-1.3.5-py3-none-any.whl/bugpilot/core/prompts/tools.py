"""Tool and Capability Prompts"""

ADVANCED_TOOL_KNOWLEDGE = """
## ADVANCED PENTESTING TOOLS (Use these intelligently!):

**Phase 1: Reconnaissance**
- `whatweb URL` - Quick tech detection
- `wafw00f URL` - WAF detection
- `nmap -sV -sC target` - Service detection

**Phase 2: Vulnerability Scanning**
- `nikto -h URL` - Web vulnerability scanner
- `nuclei -u URL -t cves/` - CVE template scanner
- `wpscan --url URL --enumerate` - WordPress scanner
- `joomscan -u URL` - Joomla scanner

**Phase 3: Targeted Testing**
- `sqlmap -u "URL" --batch --forms` - SQL injection testing
- `xsstrike -u URL` - XSS detection
- `ffuf -u URL/FUZZ -w wordlist.txt` - Directory fuzzing
- `dirb URL` - Directory brute force

**Phase 4: Exploitation**
- `sqlmap -u "URL" --dump` - Extract database
- `msfconsole` - Metasploit framework
- Custom exploit generation

**Phase 5: Research & Intelligence (NEW)**
- `check_cve <product> <version>` - Look up known vulnerabilities
- `owasp_check <category>` - Get OWASP Top 10 attack guide

**IMPORTANT RULES:**
1. START with recon (nmap, whatweb)
2. DETECT technology (WordPress? PHP? etc.)
3. **CONSULT KNOWLEDGE BASE** for detected versions (check_cve)
4. USE SPECIFIC TOOLS for detected tech
5. TEST for vulnerabilities (sqlmap, nikto)
6. EXPLOIT when found
7. NEVER repeat the same command twice in a row
"""

TOOL_SELECTION_PROMPT = """
## INTELLIGENT TOOL SELECTION:

Based on current findings, select the BEST tool:

**Findings:**
{findings_summary}

**Available Tools:**
{available_tools}

**Selection Criteria:**
1. Technology stack detected → Use specific scanner
2. Vulnerability type suspected → Use targeted tool
3. Depth of testing needed → Balance speed vs thoroughness

**Choose ONE tool that will:**
- Provide maximum value
- Not duplicate previous actions
- Move towards exploitation

**Selected Tool:** [Your choice]
**Reason:** [Why this is the best choice]
**Expected Output:** [What you'll learn]
"""
