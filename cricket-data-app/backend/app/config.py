from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Main application settings"""
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Settings
    api_title: str = Field(default="Cricket Data API", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    api_debug: bool = Field(default=True, env="API_DEBUG")
    api_host: str = Field(default="127.0.0.1", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Database Settings
    database_path: str = Field(default="cricket_data.db", env="DATABASE_PATH")
    database_echo: bool = Field(default=True, env="DATABASE_ECHO")
    
    # CORS Settings
    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5500",
        env="CORS_ALLOWED_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # Data Settings
    data_directory: str = Field(default="data", env="DATA_DIRECTORY")
    games_csv_file: str = Field(default="games.csv", env="GAMES_CSV_FILE")
    venues_csv_file: str = Field(default="venues.csv", env="VENUES_CSV_FILE")
    simulations_csv_file: str = Field(default="simulations.csv", env="SIMULATIONS_CSV_FILE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Allow extra fields without validation errors
    }
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment is one of allowed values"""
        allowed_envs = ['development', 'production']
        if v.lower() not in allowed_envs:
            raise ValueError(f'Environment must be one of: {allowed_envs}')
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
    
    # Properties for convenient access
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
    """Get settings with environment-specific overrides"""
    if settings.environment == "production":
        # Production overrides
        settings.api_debug = False
        settings.api_reload = False
        settings.api_host = "0.0.0.0"  # Accept connections from any host
        settings.database_echo = False
        settings.cors_allowed_origins = "https://your-production-domain.com"
    else:  # development (default)
        # Development overrides
        settings.api_debug = True
        settings.api_reload = True
        settings.api_host = "127.0.0.1"  # Local development only
        settings.database_echo = True
        settings.cors_allowed_origins = "http://localhost:3000,http://localhost:5500"
    
    return settings