"""
Configuration management for the Trello Sprint Generator.
"""

import json
import os
from typing import Optional
from .models import TrelloConfig


class ConfigManager:
    """Manages configuration loading and validation"""
    
    @staticmethod
    def load_config() -> TrelloConfig:
        """Load Trello configuration from multiple sources in priority order"""
        # Priority 1: Environment variables
        api_key = os.getenv('TRELLO_API_KEY')
        token = os.getenv('TRELLO_TOKEN')
        
        if api_key and token:
            config = TrelloConfig(api_key=api_key, token=token)
            if config.validate():
                return config
        
        # Priority 2: Secrets file
        config = ConfigManager._load_from_secrets_file()
        if config and config.validate():
            return config
        
        # Priority 3: Config file (fallback)
        config = ConfigManager._load_from_config_file()
        if config and config.validate():
            return config
        
        raise ConfigError(
            "Trello API credentials not found. Please set TRELLO_API_KEY and TRELLO_TOKEN "
            "environment variables, create secrets.env file, or create trello_config.json"
        )
    
    @staticmethod
    def _load_from_secrets_file() -> Optional[TrelloConfig]:
        """Load configuration from secrets.env file"""
        # Try multiple locations for secrets file
        secrets_locations = [
            'config/secrets.env',  # New organized location
            'secrets.env',         # Legacy location
            '.env'                 # Alternative naming
        ]
        
        secrets_file = None
        for location in secrets_locations:
            if os.path.exists(location):
                secrets_file = location
                break
        
        if not secrets_file:
            return None
        
        try:
            api_key = None
            token = None
            
            with open(secrets_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key == 'TRELLO_API_KEY':
                            api_key = value.strip()
                        elif key == 'TRELLO_TOKEN':
                            token = value.strip()
            
            if api_key and token:
                return TrelloConfig(api_key=api_key, token=token)
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _load_from_config_file() -> Optional[TrelloConfig]:
        """Load configuration from trello_config.json file"""
        # Try multiple locations for config file
        config_locations = [
            'config/trello_config.json',  # New organized location
            'trello_config.json'           # Legacy location
        ]
        
        config_file = None
        for location in config_locations:
            if os.path.exists(location):
                config_file = location
                break
        
        if not config_file:
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                api_key = config_data.get('api_key')
                token = config_data.get('token')
                
                if api_key and token:
                    return TrelloConfig(api_key=api_key, token=token)
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def create_template_config() -> None:
        """Create a template configuration file"""
        template = {
            "api_key": "your_api_key_here",
            "token": "your_token_here",
            "board_id": "your_board_id_here"
        }
        
        with open('trello_config.json.template', 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)


class ConfigError(Exception):
    """Configuration-related errors"""
    pass
