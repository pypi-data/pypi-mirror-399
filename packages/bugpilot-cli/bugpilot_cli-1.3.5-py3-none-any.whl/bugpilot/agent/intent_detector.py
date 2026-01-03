"""Intent Detector - Determines user's goal from input"""

from typing import Dict


class IntentDetector:
    """Detects user intent using LLM"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def detect(self, user_input: str) -> Dict[str, any]:
        """Detect intent and confidence"""
        
        prompt = f"""Analyze this user input and determine intent:

Input: "{user_input}"

Classify as ONE of:
- GREETING: Simple hi/hello
- QUESTION: Asking for information  
- SINGLE_COMMAND: One-shot command execution
- AUTONOMOUS: Complex multi-step pentesting

Respond in format:
INTENT: <type>
CONFIDENCE: <0.0-1.0>
REASON: <brief reason>"""

        response = self.llm.generate(prompt, [])
        
        # Parse response
        intent_type = "SINGLE_COMMAND"  # default
        confidence = 0.5
        
        for line in response.split('\n'):
            if line.startswith('INTENT:'):
                intent_type = line.split(':')[1].strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.split(':')[1].strip())
                except:
                    pass
        
        return {
            'type': intent_type,
            'confidence': confidence,
            'raw_input': user_input
        }
