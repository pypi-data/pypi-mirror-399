"""Configuration loader"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Config manager for settings.yaml with compatibility methods"""
    
    def __init__(self):
        # Use package directory for zero-setup config
        self.config_dir = Path(__file__).parent
        self.config_path = self.config_dir / "settings.yaml"
        self.defaults_path = self.config_dir / "defaults.yaml"
        
        self.config = {}
        # Try to ensure config exists, but don't crash if read-only
        if not self.config_path.exists() and self.defaults_path.exists():
            try:
                import shutil
                shutil.copy(self.defaults_path, self.config_path)
            except PermissionError:
                # If site-packages is read-only, we will just load defaults later
                pass
            except Exception:
                pass
        
        self.load()
        

    
    def _create_from_defaults(self):
        """Create from defaults"""
        defaults = Path(__file__).parent / "defaults.yaml"
        if defaults.exists():
            import shutil
            shutil.copy(defaults, self.config_path)
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Recursively update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def load(self) -> Dict[str, Any]:
        """Load configuration with layered approach (Defaults + Settings)"""
        self.config = {}
        
        try:
            # 1. Load Defaults
            if hasattr(self, 'defaults_path') and self.defaults_path.exists():
                with open(self.defaults_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            
            # 2. Layer User Settings on top
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                    self._deep_update(self.config, user_config)
                    
        except Exception:
            # Fallback to empty if critical failure, but defaults should have loaded
            if not self.config:
                self.config = {}
        
        # Load API keys
        self._load_api_keys()
        
        return self.config
    
    def save_config(self):
        """Save configuration to settings.yaml"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
    def update_model(self, provider: str, model: str):
        """Update model configuration (Compat)"""
        if 'llm' not in self.config:
            self.config['llm'] = {}
            
        self.config['llm']['default_provider'] = provider
        
        # Update specific task models if keys exist
        if 'models' in self.config['llm']:
            for task in self.config['llm']['models']:
                self.config['llm']['models'][task]['provider'] = provider
                self.config['llm']['models'][task]['model'] = model
    
    def _load_api_keys(self):
        """Load API keys from environment or file"""
        provider = self.config.get('llm', {}).get('default_provider', 'gemini')
        
        env_keys = {
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY"
        }
        
        # Try environment first
        env_key = env_keys.get(provider, "")
        key_from_env = os.getenv(env_key, "")
        
        # Then config file
        key_from_file = self.config.get('api_keys', {}).get(provider, "")
        
        # Store in config
        if 'api_keys' not in self.config:
            self.config['api_keys'] = {}
        
        self.config['api_keys'][f'{provider}_active'] = key_from_env or key_from_file
    
    def get_api_key(self, provider: str = None) -> Optional[str]:
        """Get API key"""
        if not provider:
            provider = self.config.get('llm', {}).get('default_provider', 'gemini')
        
        key = self.config.get('api_keys', {}).get(f'{provider}_active', "")
        return key if key else None
    
    def has_api_key(self) -> bool:
        """Check if API key exists"""
        return bool(self.get_api_key())
