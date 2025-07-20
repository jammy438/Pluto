"""
Updated app/config.py using centralized constants.

This version uses constants from app.constants for default values and validation
to maintain consistency across the application.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

# Import constants for default values and validation
from app.constants import (
    API, Database, FilePaths, validate_environment
)

class Settings(BaseSettings):
    """Main application settings using centralized constants"""
    
    # Environment
    environment: str = Field(default=API.Environments.DEVELOPMENT, env="ENVIRONMENT")
    
    # API Settings using constants
    api_title: str = Field(default=API.DEFAULT_TITLE, env="API_TITLE")
    api_version: str = Field(default=API.DEFAULT_VERSION, env="API_VERSION")
    api_debug: bool = Field(default=True, env="API_DEBUG")
    api_host: str = Field(default=API.DEFAULT_HOST, env="API_HOST")
    api_port: int = Field(default=API.DEFAULT_PORT, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Database Settings using constants
    database_path: str = Field(default=Database.DEFAULT_DATABASE_NAME, env="DATABASE_PATH")
    database_echo: bool = Field(default=True, env="DATABASE_ECHO")
    
    # CORS Settings using constants
    cors_allowed_origins: str = Field(
        default=API.CORS.DEFAULT_ORIGINS_DEV,
        env="CORS_ALLOWED_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # Data Settings using constants
    data_directory: str = Field(default=FilePaths.DEFAULT_DATA_DIRECTORY, env="DATA_DIRECTORY")
    games_csv_file: str = Field(default=FilePaths.CSVFiles.GAMES, env="GAMES_CSV_FILE")
    venues_csv_file: str = Field(default=FilePaths.CSVFiles.VENUES, env="VENUES_CSV_FILE")
    simulations_csv_file: str = Field(default=FilePaths.CSVFiles.SIMULATIONS, env="SIMULATIONS_CSV_FILE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Allow extra fields without validation errors
    }
    
    @field_validator('environment')
    @classmethod
    def validate_environment_setting(cls, v):
        """Validate environment is one of allowed values using constants"""
        if not validate_environment(v):
            raise ValueError(f'Environment must be one of: {API.Environments.VALID_ENVIRONMENTS}')
        return v.lower()
    
    @field_validator('database_path')
    @classmethod
    def validate_database_path(cls, v):
        """Ensure database directory exists"""
        db_path = Path(v)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return str(db_path)
    
    @field_validator('data_directory')
    @classmethod
    def validate_data_directory(cls, v):
        """Ensure data directory exists"""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    # Properties for convenient access using constants
    @property
    def games_path(self) -> str:
        return os.path.join(self.data_directory, self.games_csv_file)
    
    @property
    def venues_path(self) -> str:
        return os.path.join(self.data_directory, self.venues_csv_file)
    
    @property
    def simulations_path(self) -> str:
        return os.path.join(self.data_directory, self.simulations_csv_file)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into list"""
        return [origin.strip() for origin in self.cors_allowed_origins.split(',')]

# Global settings instance
settings = Settings()

def get_environment_settings() -> Settings:
    """Get settings with environment-specific overrides using constants"""
    if settings.environment == API.Environments.PRODUCTION:
        # Production overrides using constants
        settings.api_debug = False
        settings.api_reload = False
        settings.api_host = "0.0.0.0"  # Accept connections from any host
        settings.database_echo = False
        settings.cors_allowed_origins = API.CORS.DEFAULT_ORIGINS_PROD
    else:  # development (default)
        # Development overrides using constants
        settings.api_debug = True
        settings.api_reload = True
        settings.api_host = API.DEFAULT_HOST  # Local development only
        settings.database_echo = True
        settings.cors_allowed_origins = API.CORS.DEFAULT_ORIGINS_DEV
    
    return settings