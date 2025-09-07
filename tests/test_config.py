"""
Tests for configuration management.
"""

import pytest
import tempfile
import os
from src.config import ConfigManager, ConfigError
from src.models import TrelloConfig


class TestConfigManager:
    """Test cases for ConfigManager"""
    
    def test_load_from_environment(self, monkeypatch):
        """Test loading configuration from environment variables"""
        monkeypatch.setenv('TRELLO_API_KEY', 'test_api_key')
        monkeypatch.setenv('TRELLO_TOKEN', 'test_token')
        
        config = ConfigManager.load_config()
        
        assert config.api_key == 'test_api_key'
        assert config.token == 'test_token'
        assert config.validate()
    
    def test_load_from_secrets_file(self):
        """Test loading configuration from secrets.env file"""
        # Create temporary secrets file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write("TRELLO_API_KEY=test_api_key\n")
            f.write("TRELLO_TOKEN=test_token\n")
            temp_file = f.name
        
        try:
            # Temporarily rename the file to secrets.env
            secrets_file = 'secrets.env'
            os.rename(temp_file, secrets_file)
            
            # Clear environment variables
            if 'TRELLO_API_KEY' in os.environ:
                del os.environ['TRELLO_API_KEY']
            if 'TRELLO_TOKEN' in os.environ:
                del os.environ['TRELLO_TOKEN']
            
            config = ConfigManager.load_config()
            
            assert config.api_key == 'test_api_key'
            assert config.token == 'test_token'
            
        finally:
            # Clean up
            if os.path.exists(secrets_file):
                os.unlink(secrets_file)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        valid_config = TrelloConfig(api_key="valid_key_123", token="valid_token_123")
        assert valid_config.validate()
        
        # Invalid config - empty values
        invalid_config = TrelloConfig(api_key="", token="")
        assert not invalid_config.validate()
        
        # Invalid config - too short
        short_config = TrelloConfig(api_key="123", token="456")
        assert not short_config.validate()
    
    def test_config_error_when_no_credentials(self):
        """Test that ConfigError is raised when no credentials are found"""
        # Clear environment variables
        if 'TRELLO_API_KEY' in os.environ:
            del os.environ['TRELLO_API_KEY']
        if 'TRELLO_TOKEN' in os.environ:
            del os.environ['TRELLO_TOKEN']
        
        # Remove secrets file if it exists
        if os.path.exists('secrets.env'):
            os.unlink('secrets.env')
        
        # Remove config file if it exists
        if os.path.exists('trello_config.json'):
            os.unlink('trello_config.json')
        
        with pytest.raises(ConfigError):
            ConfigManager.load_config()
