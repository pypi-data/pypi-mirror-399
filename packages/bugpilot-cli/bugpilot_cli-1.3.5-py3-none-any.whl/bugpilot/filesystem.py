"""
File System Access Module - Gemini CLI-like capabilities
Allows the agent to read, analyze, and interact with files in the working directory
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import mimetypes


class FileSystemAccess:
    """Provides file system access for the agent"""
    
    def __init__(self, working_directory: str = "."):
        self.working_directory = Path(working_directory).resolve()
        self.accessible_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go',
            '.rb', '.php', '.swift', '.kt', '.rs', '.scala', '.sh', '.bash',
            '.txt', '.md', '.json', '.yaml', '.yml', '.xml', '.html', '.css',
            '.sql', '.config', '.conf', '.ini', '.env', '.log'
        }
    
    def set_working_directory(self, path: str):
        """Set the working directory"""
        new_path = Path(path).resolve()
        if new_path.exists() and new_path.is_dir():
            self.working_directory = new_path
            return True
        return False
    
    def get_current_directory(self) -> str:
        """Get current working directory"""
        return str(self.working_directory)
    
    def list_files(self, pattern: str = "*", recursive: bool = False) -> List[Dict[str, str]]:
        """List files in the working directory"""
        files = []
        
        if recursive:
            file_paths = self.working_directory.rglob(pattern)
        else:
            file_paths = self.working_directory.glob(pattern)
        
        for file_path in file_paths:
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(self.working_directory)),
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix,
                    "modified": file_path.stat().st_mtime
                })
        
        return files
    
    def read_file(self, file_path: str, max_lines: Optional[int] = None) -> Tuple[bool, str]:
        """Read file contents"""
        try:
            full_path = (self.working_directory / file_path).resolve()
            
            # Security check - ensure file is within working directory
            if not str(full_path).startswith(str(self.working_directory)):
                return False, "Access denied: File outside working directory"
            
            if not full_path.exists():
                return False, f"File not found: {file_path}"
            
            # Check if text file
            if full_path.suffix not in self.accessible_extensions:
                return False, f"Cannot read file type: {full_path.suffix}"
            
            # Read file
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                if max_lines:
                    lines = [f.readline() for _ in range(max_lines)]
                    content = ''.join(lines)
                else:
                    content = f.read()
            
            return True, content
            
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def write_file(self, file_path: str, content: str) -> Tuple[bool, str]:
        """Write content to file"""
        try:
            full_path = (self.working_directory / file_path).resolve()
            
            # Security check
            if not str(full_path).startswith(str(self.working_directory)):
                return False, "Access denied: File outside working directory"
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"File written: {file_path}"
            
        except Exception as e:
            return False, f"Error writing file: {str(e)}"
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get detailed file information"""
        try:
            full_path = (self.working_directory / file_path).resolve()
            
            if not full_path.exists():
                return None
            
            stat = full_path.stat()
            
            return {
                "name": full_path.name,
                "path": str(file_path),
                "absolute_path": str(full_path),
                "size": stat.st_size,
                "size_human": self._human_readable_size(stat.st_size),
                "extension": full_path.suffix,
                "is_file": full_path.is_file(),
                "is_dir": full_path.is_dir(),
                "modified": stat.st_mtime,
                "mime_type": mimetypes.guess_type(str(full_path))[0]
            }
            
        except Exception:
            return None
    
    def search_files(self, query: str, extension: Optional[str] = None) -> List[str]:
        """Search for files by name"""
        results = []
        
        pattern = f"*{query}*"
        if extension:
            pattern += extension
        
        for file_path in self.working_directory.rglob(pattern):
            if file_path.is_file():
                results.append(str(file_path.relative_to(self.working_directory)))
        
        return results
    
    def get_directory_tree(self, max_depth: int = 3, current_depth: int = 0) -> str:
        """Get directory tree structure"""
        if current_depth >= max_depth:
            return ""
        
        tree = []
        indent = "  " * current_depth
        
        try:
            items = sorted(self.working_directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            
            for item in items[:50]:  # Limit to 50 items
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    tree.append(f"{indent}[DIR] {item.name}/")
                else:
                    size = self._human_readable_size(item.stat().st_size)
                    tree.append(f"{indent}[FILE] {item.name} ({size})")
        
        except Exception as e:
            tree.append(f"{indent}[Error: {str(e)}]")
        
        return "\n".join(tree)
    
    def analyze_project(self) -> Dict[str, any]:
        """Analyze the current project structure"""
        analysis = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "languages": {},
            "largest_files": [],
        }
        
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
        }
        
        files_with_size = []
        
        for file_path in self.working_directory.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                analysis['total_files'] += 1
                size = file_path.stat().st_size
                analysis['total_size'] += size
                
                ext = file_path.suffix
                analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    analysis['languages'][lang] = analysis['languages'].get(lang, 0) + 1
                
                files_with_size.append((str(file_path.relative_to(self.working_directory)), size))
        
        # Get largest files
        files_with_size.sort(key=lambda x: x[1], reverse=True)
        analysis['largest_files'] = [
            {"file": f, "size": self._human_readable_size(s)}
            for f, s in files_with_size[:10]
        ]
        
        return analysis
    
    @staticmethod
    def _human_readable_size(size: int) -> str:
        """Convert size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
