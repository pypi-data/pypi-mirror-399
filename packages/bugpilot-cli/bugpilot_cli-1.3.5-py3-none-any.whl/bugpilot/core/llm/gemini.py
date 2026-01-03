"""Gemini Model Implementation"""

import os
import warnings
import logging
from typing import List, Dict, Optional
from .base import BaseModel

# Suppress Google API deprecation using warnings filter
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", module="google.generativeai")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GeminiModel(BaseModel):
    """Google Gemini model integration"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        if genai and hasattr(genai, 'configure'):
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
            
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Gemini"""
        if not self.model:
            return "Error: google-generativeai package not installed."
            
        try:
            if context and len(context) > 0:
                history = []
                for msg in context:
                    history.append({
                        'role': 'user' if msg['role'] == 'user' else 'model', 
                        'parts': [msg['content']]
                    })
                
                chat = self.model.start_chat(history=history)
                response = chat.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)
            
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"
