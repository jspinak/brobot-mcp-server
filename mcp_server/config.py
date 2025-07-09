"""Configuration module for the MCP server."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, validator, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="MCP_HOST")
    port: int = Field(default=8000, env="MCP_PORT")
    reload: bool = Field(default=True, env="MCP_RELOAD")
    log_level: str = Field(default="info", env="MCP_LOG_LEVEL")
    
    # Brobot CLI settings
    brobot_cli_jar: Optional[str] = Field(default=None, env="BROBOT_CLI_JAR")
    java_executable: str = Field(default="java", env="JAVA_EXECUTABLE")
    cli_timeout: float = Field(default=30.0, env="CLI_TIMEOUT")
    use_mock_data: bool = Field(default=True, env="USE_MOCK_DATA")
    
    # API settings
    api_version: str = Field(default="v1", env="API_VERSION")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @validator("brobot_cli_jar")
    def validate_jar_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate and resolve the JAR path."""
        if v is None:
            # Try to find the JAR in common locations
            possible_paths = [
                Path("brobot-cli.jar"),
                Path("brobot-cli/build/libs/brobot-cli.jar"),
                Path("../brobot-cli.jar"),
                Path("/app/brobot-cli.jar"),  # Docker location
            ]
            
            for path in possible_paths:
                if path.exists():
                    return str(path.absolute())
            
            return None
        
        # Resolve the provided path
        path = Path(v)
        if not path.is_absolute():
            path = path.absolute()
        
        return str(path)
    
    @validator("port")
    def validate_port(cls, v: int) -> int:
        """Validate port number is in valid range."""
        if v <= 0 or v > 65535:
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    @validator("cli_timeout")
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError(f"Timeout must be positive, got {v}")
        return v
    
    @property
    def is_cli_configured(self) -> bool:
        """Check if the CLI is properly configured."""
        return (
            self.brobot_cli_jar is not None and 
            Path(self.brobot_cli_jar).exists() and
            not self.use_mock_data
        )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings