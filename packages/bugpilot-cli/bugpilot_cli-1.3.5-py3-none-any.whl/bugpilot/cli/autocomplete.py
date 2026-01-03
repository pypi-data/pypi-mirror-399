"""
Enhanced Input Module - Autocomplete for commands and files
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from typing import List, Iterable
import os


class BugPilotCompleter(Completer):
    """Custom completer for BugPilot CLI with command and file suggestions"""
    
    COMMANDS = [
        "/help", "/settings", "/mode", "/model", "/output", "/autopilot",
        "/save", "/export", "/sessions", "/load", "/history",
        "/tokens", "/stream", "/reset", "/clear", "/exit", "/quit",
        "/update", "/cve", "/owasp"
    ]
    
    def __init__(self, working_directory: str = "."):
        self.working_directory = working_directory
        self.path_completer = PathCompleter(only_directories=False, expanduser=True)
    
    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        text = document.text_before_cursor
        
        # Command completion with /
        if text.startswith('/'):
            word = text[1:]  # Remove the /
            for cmd in self.COMMANDS:
                if cmd[1:].startswith(word.lower()):
                    yield Completion(
                        cmd[1:],  # Complete without /
                        start_position=-len(word),
                        display=cmd,
                        display_meta="Command"
                    )
        
        # File completion with @
        elif '@' in text:
            # Get text after last @
            parts = text.rsplit('@', 1)
            if len(parts) == 2:
                prefix, file_part = parts
                
                # Use PathCompleter for file suggestions
                try:
                    files = []
                    search_dir = self.working_directory
                    
                    # Get files in working directory
                    if os.path.exists(search_dir):
                        for item in os.listdir(search_dir):
                            item_path = os.path.join(search_dir, item)
                            if os.path.isfile(item_path) and item.lower().startswith(file_part.lower()):
                                files.append(item)
                    
                    for file in files[:10]:  # Limit to 10 suggestions
                        if file.startswith(file_part):
                            yield Completion(
                                file,
                                start_position=-len(file_part),
                                display=f"@{file}",
                                display_meta="File"
                            )
                except:
                    pass
        
        # Folder completion with #
        elif '#' in text:
            parts = text.rsplit('#', 1)
            if len(parts) == 2:
                prefix, folder_part = parts
                
                try:
                    folders = []
                    search_dir = self.working_directory
                    
                    if os.path.exists(search_dir):
                        for item in os.listdir(search_dir):
                            item_path = os.path.join(search_dir, item)
                            if os.path.isdir(item_path) and item.lower().startswith(folder_part.lower()):
                                folders.append(item)
                    
                    for folder in folders[:10]:
                        if folder.startswith(folder_part):
                            yield Completion(
                                folder,
                                start_position=-len(folder_part),
                                display=f"#{folder}",
                                display_meta="Folder"
                            )
                except:
                    pass


def get_user_input_with_autocomplete(
    prompt_text: str,
    working_directory: str = ".",
    multiline: bool = False,
    **kwargs
) -> str:
    """
    Get user input with intelligent autocomplete
    
    Features:
    - /command - Shows command suggestions
    - @file - Shows file suggestions
    - #folder - Shows folder suggestions
    """
    completer = BugPilotCompleter(working_directory)
    
    try:
        result = prompt(
            prompt_text,
            completer=completer,
            complete_while_typing=True,
            multiline=multiline,
            **kwargs
        )
        return result
    except (KeyboardInterrupt, EOFError):
        return ""
    except Exception as e:
        # Fallback to regular input
        return input(prompt_text)


# Helper functions for specific use cases
def get_command_input(prompt_text: str = "[+] You: ", **kwargs) -> str:
    """Get input with command autocomplete"""
    return get_user_input_with_autocomplete(prompt_text, **kwargs)


def get_file_input(prompt_text: str, working_directory: str = ".") -> str:
    """Get input with file autocomplete"""
    return get_user_input_with_autocomplete(prompt_text, working_directory)
