"""Hacker Mode - Autonomous pentesting (Unified Session)"""

import time
import re
import json
from typing import List, Dict
from bugpilot.core.prompts import get_system_prompt
from bugpilot.core.state.session import SessionManager
from bugpilot.core.state.memory import DynamicContext

class HackerMode:
    """Advanced autonomous mode - Persistent Session"""
    
    def __init__(self, controller, ui, config):
        self.controller = controller
        self.ui = ui
        self.config = config
        self.session_manager = SessionManager()
        self.dynamic_context = DynamicContext()
        
        # Persistent State
        self.history = []
        self.findings = []
        self.iteration = 0
    
    def chat(self, user_input: str):
        """Process user input and loop autonomously until input needed"""
        from bugpilot.tools.knowledge import search_cve, get_owasp_info
        
        # Add user input to history
        self.history.append({"role": "user", "content": user_input})
        
        # System prompt
        system_prompt = get_system_prompt("hacker")
        
        # Autonomous Loop (Limit to avoid infinite costs/loops, e.g., 5 steps per input)
        # But user wants "dynamic flow". Let's use a soft limit or stop on conversational output.
        MAX_AUTO_STEPS = 10 
        steps = 0
        
        while steps < MAX_AUTO_STEPS:
            steps += 1
            self.iteration += 1
            
            # Context
            prompt_content = system_prompt.format(
                previous_findings="\n".join(self.findings) if self.findings else "None",
                current_iteration=self.iteration,
                max_iterations="Unlimited",
                actions_count=len(self.history) // 2,
                failures=0,
                tools=self.dynamic_context.get_tool_arsenal()
            ) 
            
            # Add dynamic instructions regarding file operations
            prompt_content += "\n\n**CAPABILITIES:**\n"
            prompt_content += "- RUN COMMANDS: Use `cmd` field. (e.g. `nmap ...`, `cat ...`, `echo '...' > file`).\n"
            prompt_content += "- FILE OPS: Read/Write files using shell commands.\n"
            prompt_content += "- KNOWLEDGE: `cve_search`, `owasp_info`.\n"
            prompt_content += "- LOGIC: If you need to run multiple commands, output one, wait for execution, then output the next in the subsequent turn (Automatic).\n"
            prompt_content += "- STOP: If you need to ask the user something or show results, set `cmd` to `None`.\n"

            
            recent_history = self.history[-15:] # Keep moderate context window
            
            # Check LLM
            if not hasattr(self.controller, 'reasoning_llm') or not self.controller.reasoning_llm:
                 self.ui.print_error("No Reasoning LLM available.")
                 return
                 
            # Generate
            with self.ui.loading_indicator("Thinking..."):
                response = self.controller.reasoning_llm.generate(prompt_content, recent_history)
            
            # Parse
            command = None
            thought = None
            cmd_timeout = None
            
            try:
                # 1. Try to find markdown block
                json_str = None
                md_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                if md_match:
                    json_str = md_match.group(1)
                else:
                    # 2. Try to find raw JSON object
                    start = response.find('{')
                    end = response.rfind('}')
                    if start != -1 and end != -1:
                        json_str = response[start:end+1]
                
                if json_str:
                    json_data = json.loads(json_str)
                    command = json_data.get('cmd', '').strip()
                    if command.lower() == 'none' or command.lower() == 'null': command = None 
                    thought = json_data.get('thought', '')
                    cmd_timeout = json_data.get('timeout')
                    if cmd_timeout: cmd_timeout = int(cmd_timeout)
                    
                    status = json_data.get('status', 'single').upper()
                    
                    # If we are effectively looping autonomously, mark as continuous
                    if steps > 1:
                        status = "CONTINUOUS"
                    
                    if thought:
                        self.ui.print_panel(thought, title="BugPilot AI", style="cyan")
            except Exception as e:
                # Fallback regex for pure command if JSON fails
                cmd_match = re.search(r'```(?:bash|sh|powershell)?\s*(.*?)```', response, re.DOTALL)
                if cmd_match:
                    command = cmd_match.group(1).strip()
                
                # Check loop state for status
                status = "CONTINUOUS" if steps > 1 else "SINGLE"
                
                # If parsing fails or we just have raw text
                if not command and not thought:
                     # Strip JSON parts if we act as fallback to avoid printing raw JSON
                     clean_response = response
                     if '{' in response and '}' in response:
                         # Attempt to recover thought from broken JSON
                         t_match = re.search(r'"thought":\s*"(.*?)"', response)
                         if t_match: clean_response = t_match.group(1)
                     
                     self.ui.type_text(clean_response)
            
            # Add Assistant Response to History
            self.history.append({"role": "assistant", "content": response})

            # DECISION: Stop or Continue?
            if not command or command == "COMPLETE":
                if command == "COMPLETE":
                    self.ui.print_success("Objective Completed.")
                return # Give control back to USER
            
            # EXECUTION
            if command:
                title_text = f"Proposed Action [{status}]"
                self.ui.print_panel(command, title=title_text, style="bold green")
                
                # Check for internal tools
                if command.startswith("cve_search") or command.startswith("owasp_info"):
                    output = ""
                    if command.startswith("cve_search"):
                         q = command.replace("cve_search", "").strip()
                         output = search_cve(q)
                    else:
                         q = command.replace("owasp_info", "").strip()
                         output = get_owasp_info(q)
                    
                    self.ui.print_panel(output, title="Knowledge Base", style="info")
                    self.history.append({"role": "user", "content": f"Tool Result:\n{output}"})
                    continue # Loop immediately
                
                # Exec Shell
                auto_exec = self.config.get('auto_execute_commands', False)
                allowed = True
                
                if not auto_exec:
                    # Interactive Prompt: Allow Y/n OR text feedback
                    feedback = self.ui.get_input("Execute? [Y/n] or type instruction: ")
                    
                    if feedback.lower() in ['', 'y', 'yes']:
                        allowed = True
                    elif feedback.lower() in ['n', 'no']:
                        allowed = False
                        self.ui.print_warning("Skipped.")
                        self.history.append({"role": "user", "content": "Action skipped by user."})
                        continue
                    else:
                        # User provided feedback/instruction
                        allowed = False
                        self.ui.print_info("Replanning based on feedback...")
                        self.history.append({"role": "user", "content": f"User Feedback/Instruction: {feedback}"})
                        continue
                
                if allowed:
                    with self.ui.loading_indicator(f"Executing: {command}"):
                        execution_result = self.controller.executor.execute(command, timeout=cmd_timeout)
                    
                    output = execution_result.get('output', '')
                    success = execution_result.get('success', False)
                    
                    # Truncate for display
                    truncated_output = output[:2000] 
                    if len(output) > 2000: truncated_output += "\n...[Output Truncated]..."
                    self.ui.print_panel(f"```text\n{truncated_output}\n```", title="Command Output", style="white")
                    
                    # Add result to history
                    self.history.append({
                        "role": "user", 
                        "content": f"Command executed.\nExit Code: {execution_result.get('returncode')}\nOutput:\n{output[:4000]}"
                    })
                    
                    self.findings.append(f"Ran `{command}` - Success: {success}")
                    
                    # CONTINUE LOOP (Autonomous)
                else:
                    self.ui.print_warning("Skipped.")
                    self.history.append({"role": "user", "content": "Command skipped by user."})
                    return # Return to user to ask what to do next
