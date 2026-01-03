"""
Context Manager for BugPilot CLI
Smart context storage and optimization - only keep what's needed
Like Gemini CLI's context management
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import hashlib


class ContextManager:
    """Manages conversation context efficiently"""
    
    def __init__(self, max_context_tokens=8000):
        self.max_context_tokens = max_context_tokens
        self.context = []
        self.file_references = {}
        self.folder_references = {}
        self.important_findings = []
        self.current_working_dir = os.getcwd()
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to context with smart truncation"""
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "token_count": self._estimate_tokens(content)
        }
        
        self.context.append(message)
        self._optimize_context()
    
    def add_file_reference(self, filepath: str, purpose: str = "analysis"):
        """Add file to context for analysis"""
        path = Path(filepath)
        if not path.exists():
            return False
        
        # Read file with smart truncation
        content = self._read_file_smart(path)
        file_hash = self._hash_file(path)
        
        self.file_references[str(path)] = {
            "path": str(path),
            "name": path.name,
            "size": path.stat().st_size,
            "content": content,
            "hash": file_hash,
            "purpose": purpose,
            "analyzed": False
        }
        return True
    
    def add_folder_reference(self, folderpath: str, purpose: str = "scan"):
        """Add folder to context for scanning"""
        path = Path(folderpath)
        if not path.exists() or not path.is_dir():
            return False
        
        # Get folder structure
        structure = self._get_folder_structure(path)
        
        self.folder_references[str(path)] = {
            "path": str(path),
            "structure": structure,
            "file_count": len(structure['files']),
            "purpose": purpose,
            "analyzed": False
        }
        return True
    
    def add_finding(self, finding: Dict):
        """Add important finding (always keep in context)"""
        finding['priority'] = finding.get('severity', 'medium')
        self.important_findings.append(finding)
    
    def get_relevant_context(self, query: str) -> List[Dict]:
        """Get only relevant context for current query"""
        # Always include important findings
        context = [{"role": "system", "content": self._format_findings()}]
        
        # Add file references if mentioned
        for filepath in self.file_references:
            if filepath.lower() in query.lower() or self.file_references[filepath]['purpose'] in query.lower():
                context.append({
                    "role": "system",
                    "content": f"File: {filepath}\n{self.file_references[filepath]['content'][:2000]}"
                })
        
        # Add recent conversation (last 5 messages)
        context.extend(self.context[-5:])
        
        return context
    
    def _optimize_context(self):
        """Optimize context to stay within token limit"""
        total_tokens = sum(msg.get('token_count', 0) for msg in self.context)
        
        if total_tokens > self.max_context_tokens:
            # Keep first message (system prompt) and last N messages
            if len(self.context) > 10:
                # Summarize middle messages
                summary = self._summarize_messages(self.context[1:-5])
                self.context = [
                    self.context[0],  # System prompt
                    {"role": "system", "content": f"Previous context summary: {summary}", "token_count": 100},
                    *self.context[-5:]  # Last 5 messages
                ]
    
    def _summarize_messages(self, messages: List[Dict]) -> str:
        """Summarize messages to reduce tokens"""
        # Extract key information
        findings = []
        commands = []
        
        for msg in messages:
            content = msg.get('content', '')
            if 'vulnerability' in content.lower() or 'finding' in content.lower():
                findings.append(content[:200])
            if msg.get('role') == 'assistant' and 'command' in content.lower():
                commands.append(content[:100])
        
        summary = f"Found {len(findings)} potential issues. Executed {len(commands)} commands."
        return summary
    
    def _read_file_smart(self, path: Path, max_lines=500) -> str:
        """Read file with smart truncation"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            if len(lines) <= max_lines:
                return ''.join(lines)
            
            # Take first 250 and last 250 lines
            return ''.join(lines[:250]) + f"\n... [{len(lines) - 500} lines omitted] ...\n" + ''.join(lines[-250:])
        except:
            return "[Binary file or read error]"
    
    def _get_folder_structure(self, path: Path, max_depth=3) -> Dict:
        """Get folder structure efficiently"""
        structure = {
            "files": [],
            "folders": [],
            "total_size": 0
        }
        
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    structure["files"].append({
                        "path": str(item.relative_to(path)),
                        "size": item.stat().st_size,
                        "ext": item.suffix
                    })
                    structure["total_size"] += item.stat().st_size
                elif item.is_dir():
                    structure["folders"].append(str(item.relative_to(path)))
        except:
            pass
        
        return structure
    
    def _hash_file(self, path: Path) -> str:
        """Hash file for deduplication"""
        try:
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()[:16]
        except:
            return "unknown"
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text) // 4
    
    def _format_findings(self) -> str:
        """Format important findings for context"""
        if not self.important_findings:
            return "No critical findings yet."
        
        formatted = "Important Findings:\n"
        for i, finding in enumerate(self.important_findings[-5:], 1):  # Last 5
            formatted += f"{i}. [{finding.get('severity', 'medium').upper()}] {finding.get('title', 'Finding')}\n"
        
        return formatted
    
    def clear_context(self):
        """Clear non-essential context"""
        self.context = self.context[-3:]  # Keep last 3 messages
        # Keep file/folder references and findings
    
    def export_context(self, filepath: str):
        """Export full context to file"""
        data = {
            "context": self.context,
            "files": self.file_references,
            "folders": self.folder_references,
            "findings": self.important_findings
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
