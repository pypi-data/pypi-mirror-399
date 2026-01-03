"""Controller - Main agent orchestration"""

from .intent_detector import IntentDetector
from .executor import Executor


class Controller:
    """Main controller orchestrating agent components"""
    
    def __init__(self, llms: dict, config, ui):
        self.intent_detector = IntentDetector(llms['intent'])
        self.executor = Executor(config.safety, timeout=600)
        self.reasoning_llm = llms['reasoning']
        self.ui = ui
        self.config = config
    
    def process(self, user_input: str) -> dict:
        """Process user input through agent pipeline"""
        
        # 1. Detect intent
        intent = self.intent_detector.detect(user_input)
        
        # 2. Route based on intent
        if intent['type'] == 'GREETING':
            return {'type': 'greeting', 'response': 'Ready. Awaiting target.'}
        
        elif intent['type'] == 'QUESTION':
            response = self.reasoning_llm.generate(user_input, [])
            return {'type': 'answer', 'response': response}
        
        elif intent['type'] == 'SINGLE_COMMAND':
            # Extract and execute command
            command = self._extract_command(user_input)
            result = self.executor.execute(command)
            analysis = self._analyze_result(user_input, command, result)
            return {'type': 'execution', 'result': result, 'analysis': analysis}
        
        elif intent['type'] == 'AUTONOMOUS':
            # Delegate to hacker mode
            return {'type': 'autonomous', 'requires_hacker_mode': True}
        
        return {'type': 'unknown', 'response': 'Unable to process request'}
    
    def _extract_command(self, user_input: str) -> str:
        """Extract command from natural language"""
        prompt = f"Extract the exact command to run: {user_input}\nCommand:"
        return self.reasoning_llm.generate(prompt, []).strip()
    
    def _analyze_result(self, request: str, command: str, result: dict) -> str:
        """Analyze execution results"""
        prompt = f"""Analyze: Request: {request}
Command: {command}  
Output: {result.get('output', '')[:500]}

Brief analysis:"""
        return self.reasoning_llm.generate(prompt, [])
