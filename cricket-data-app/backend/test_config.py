import pytest
import os
from app.config import Settings, get_environment_settings

class TestConfiguration:
    """Test configuration management"""
    
    def test_default_settings(self):
        """Test default configuration values"""
        settings = Settings()
        assert settings.environment == "development"
        assert settings.api.title == "Cricket Data API"
        assert settings.database.path == "cricket_data.db"
    
    def test_environment_overrides(self, monkeypatch):
        """Test environment variable overrides"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("API_DEBUG", "false")
        monkeypatch.setenv("DATABASE_PATH", "/prod/cricket.db")
        
        settings = Settings()
        assert settings.environment == "production"
        assert settings.api.debug == False
        assert settings.database.path == "/prod/cricket.db"
    
    def test_nested_environment_variables(self, monkeypatch):
        """Test nested environment variables with delimiter"""
        monkeypatch.setenv("DATABASE__PATH", "/nested/path/cricket.db")
        monkeypatch.setenv("CORS__ALLOWED_ORIGINS", "https://example.com,https://test.com")
        
        settings = Settings()
        assert settings.database.path == "/nested/path/cricket.db"
        assert "https://example.com" in settings.cors.allowed_origins
    
    def test_production_environment_settings(self, monkeypatch):
        """Test production environment specific settings"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        
        settings = get_environment_settings()
        assert settings.environment == "production"
        assert settings.api.debug == False
        assert settings.api.reload == False
        assert settings.api.host == "0.0.0.0"
        assert settings.database.echo == False
    
    def test_development_environment_settings(self, monkeypatch):
        """Test development environment specific settings"""
        monkeypatch.setenv("ENVIRONMENT", "development")
        
        settings = get_environment_settings()
        assert settings.environment == "development"
        assert settings.api.debug == True
        assert settings.api.reload == True
        assert settings.api.host == "127.0.0.1"
        assert settings.database.echo == True
    
    def test_invalid_environment_raises_error(self, monkeypatch):
        """Test invalid environment raises validation error"""
        monkeypatch.setenv("ENVIRONMENT", "invalid")
        
        with pytest.raises(ValueError, match="Environment must be one of"):
            Settings()