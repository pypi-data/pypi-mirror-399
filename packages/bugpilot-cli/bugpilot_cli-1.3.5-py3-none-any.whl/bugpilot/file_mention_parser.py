"""
File Mention Parser for BugPilot CLI
Parse @mentions for files and folders - like modern AI CLIs
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


class FileMentionParser:
    """Parse @file and @folder mentions from user input"""
    
    def __init__(self):
        self.mention_pattern = r'@([^\s]+)'
    
    def parse_mentions(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Parse text for file/folder mentions
        
        Returns:
            - Clean text (without mentions)
            - List of mentioned files/folders
        """
        mentions = []
        clean_text = text
        
        # Find all @mentions
        matches = re.finditer(self.mention_pattern, text)
        
        for match in matches:
            mention_path = match.group(1)
            path = Path(mention_path)
            
            # Check if file or folder exists
            if path.exists():
                mention_info = {
                    "original": match.group(0),
                    "path": str(path.absolute()),
                    "type": "folder" if path.is_dir() else "file",
                    "name": path.name,
                    "size": path.stat().st_size if path.is_file() else 0
                }
                mentions.append(mention_info)
                
                # Replace mention with readable reference
                clean_text = clean_text.replace(
                    match.group(0),
                    f"[FILE: {path.name}]" if path.is_file() else f"[FOLDER: {path.name}]"
                )
        
        return clean_text, mentions
    
    def format_mention_context(self, mention: Dict) -> str:
        """Format a mention for AI context"""
        if mention['type'] == 'file':
            return self._format_file_mention(mention)
        else:
            return self._format_folder_mention(mention)
    
    def _format_file_mention(self, mention: Dict) -> str:
        """Format file mention with content"""
        path = Path(mention['path'])
        
        try:
            # Read file content (with smart truncation)
            content = self._read_file_smart(path)
            
            return f"""**File: {mention['name']}**
Path: {mention['path']}
Size: {self._human_readable_size(mention['size'])}

Content:
```
{content}
```"""
        except:
            return f"**File: {mention['name']}** (Unable to read)"
    
    def _format_folder_mention(self, mention: Dict) -> str:
        """Format folder mention with structure"""
        path = Path(mention['path'])
        
        try:
            # Get folder structure
            structure = self._get_folder_structure(path)
            
            return f"""**Folder: {mention['name']}**
Path: {mention['path']}
Files: {len(structure['files'])}
Folders: {len(structure['folders'])}

Structure:
{self._format_tree(structure)}"""
        except:
            return f"**Folder: {mention['name']}** (Unable to read)"
    
    def _read_file_smart(self, path: Path, max_lines=500) -> str:
        """Read file with smart truncation"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if len(lines) <= max_lines:
                return ''.join(lines)
            
            # First 250 and last 250 lines
            return (
                ''.join(lines[:250]) +
                f"\n... [{len(lines) - 500} lines omitted] ...\n" +
                ''.join(lines[-250:])
            )
        except:
            return "[Binary file or read error]"
    
    def _get_folder_structure(self, path: Path, max_files=100) -> Dict:
        """Get folder structure"""
        structure = {
            "files": [],
            "folders": []
        }
        
        try:
            for item in list(path.rglob('*'))[:max_files]:
                rel_path = str(item.relative_to(path))
                if item.is_file():
                    structure["files"].append(rel_path)
                elif item.is_dir():
                    structure["folders"].append(rel_path)
        except:
            pass
        
        return structure
    
    def _format_tree(self, structure: Dict) -> str:
        """Format structure as tree"""
        lines = []
        
        # Show folders
        for folder in structure['folders'][:20]:
            lines.append(f"  [DIR]  {folder}")
        
        # Show files
        for file in structure['files'][:30]:
            lines.append(f"  [FILE] {file}")
        
        if len(structure['files']) > 30:
            lines.append(f"  ... and {len(structure['files']) - 30} more files")
        
        return '\n'.join(lines) if lines else "  (empty)"
    
    def _human_readable_size(self, size: int) -> str:
        """Convert bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


# Example usage demonstrations
def demo_usage():
    """Demonstrate file mention parsing"""
    parser = FileMentionParser()
    
    # Example 1: File mention
    text1 = "Analyze @app.js for security issues"
    clean, mentions = parser.parse_mentions(text1)
    print(f"Input: {text1}")
    print(f"Clean: {clean}")
    print(f"Mentions: {mentions}\n")
    
    # Example 2: Multiple mentions
    text2 = "Compare @api.js with @auth.js and check @./config/ folder"
    clean, mentions = parser.parse_mentions(text2)
    print(f"Input: {text2}")
    print(f"Clean: {clean}")
    print(f"Mentions: {len(mentions)} items\n")
    
    # Example 3: Folder mention
    text3 = "Scan @./src for vulnerabilities"
    clean, mentions = parser.parse_mentions(text3)
    print(f"Input: {text3}")
    print(f"Clean: {clean}")
    print(f"Mentions: {mentions}")


if __name__ == "__main__":
    demo_usage()
