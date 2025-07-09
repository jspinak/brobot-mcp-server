"""Unit tests for configuration module."""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from mcp_server.config import Settings, get_settings


class TestSettings:
    """Test Settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.reload is True
        assert settings.log_level == "info"
        assert settings.java_executable == "java"
        assert settings.cli_timeout == 30.0
        assert settings.use_mock_data is True
        assert settings.api_version == "v1"
    
    def test_settings_from_env(self, monkeypatch):
        """Test settings from environment variables."""
        # Set environment variables
        monkeypatch.setenv("MCP_HOST", "127.0.0.1")
        monkeypatch.setenv("MCP_PORT", "8080")
        monkeypatch.setenv("MCP_LOG_LEVEL", "debug")
        monkeypatch.setenv("USE_MOCK_DATA", "false")
        monkeypatch.setenv("BROBOT_CLI_JAR", "/path/to/cli.jar")
        monkeypatch.setenv("CLI_TIMEOUT", "60.0")
        
        # Force reload of settings with new env vars
        from pydantic_settings import BaseSettings
        settings = Settings(
            _env_file=None,  # Don't load .env file
            host="127.0.0.1",
            port=8080,
            log_level="debug",
            use_mock_data=False,
            brobot_cli_jar="/path/to/cli.jar",
            cli_timeout=60.0
        )
        
        assert settings.host == "127.0.0.1"
        assert settings.port == 8080
        assert settings.log_level == "debug"
        assert settings.use_mock_data is False
        assert settings.brobot_cli_jar == "/path/to/cli.jar"
        assert settings.cli_timeout == 60.0
    
    def test_jar_path_validation_none(self):
        """Test JAR path validation when None."""
        settings = Settings(brobot_cli_jar=None)
        assert settings.brobot_cli_jar is None
    
    def test_jar_path_validation_absolute(self):
        """Test JAR path validation with absolute path."""
        settings = Settings(brobot_cli_jar="/absolute/path/to/cli.jar")
        assert settings.brobot_cli_jar == "/absolute/path/to/cli.jar"
    
    def test_jar_path_validation_relative(self, tmp_path, monkeypatch):
        """Test JAR path validation with relative path."""
        # Create a temp JAR file
        jar_file = tmp_path / "test.jar"
        jar_file.write_text("mock jar")
        
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        settings = Settings(brobot_cli_jar="test.jar")
        assert Path(settings.brobot_cli_jar).is_absolute()
        assert Path(settings.brobot_cli_jar).exists()
    
    def test_jar_path_auto_discovery(self, tmp_path, monkeypatch):
        """Test automatic JAR discovery."""
        # Create JAR in expected location
        cli_dir = tmp_path / "brobot-cli" / "build" / "libs"
        cli_dir.mkdir(parents=True)
        jar_file = cli_dir / "brobot-cli.jar"
        jar_file.write_text("mock jar")
        
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        settings = Settings(brobot_cli_jar=None)
        
        # Should find the JAR automatically
        assert settings.brobot_cli_jar is not None
        assert "brobot-cli.jar" in settings.brobot_cli_jar
    
    def test_is_cli_configured_true(self, tmp_path):
        """Test is_cli_configured when properly configured."""
        # Create a mock JAR file
        jar_file = tmp_path / "cli.jar"
        jar_file.write_text("mock")
        
        settings = Settings(
            brobot_cli_jar=str(jar_file),
            use_mock_data=False
        )
        
        assert settings.is_cli_configured is True
    
    def test_is_cli_configured_false_no_jar(self):
        """Test is_cli_configured when JAR missing."""
        settings = Settings(
            brobot_cli_jar=None,
            use_mock_data=False
        )
        
        assert settings.is_cli_configured is False
    
    def test_is_cli_configured_false_mock_mode(self, tmp_path):
        """Test is_cli_configured in mock mode."""
        jar_file = tmp_path / "cli.jar"
        jar_file.write_text("mock")
        
        settings = Settings(
            brobot_cli_jar=str(jar_file),
            use_mock_data=True  # Mock mode enabled
        )
        
        assert settings.is_cli_configured is False
    
    def test_is_cli_configured_false_jar_not_exists(self):
        """Test is_cli_configured when JAR doesn't exist."""
        settings = Settings(
            brobot_cli_jar="/nonexistent/path.jar",
            use_mock_data=False
        )
        
        assert settings.is_cli_configured is False
    
    def test_env_file_loading(self, tmp_path, monkeypatch):
        """Test loading settings from .env file."""
        # Create .env file
        env_content = """
MCP_HOST=192.168.1.1
MCP_PORT=9000
USE_MOCK_DATA=false
BROBOT_CLI_JAR=custom.jar
"""
        env_file = tmp_path / ".env"
        env_file.write_text(env_content)
        
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        # Clear any existing env vars
        for key in ["MCP_HOST", "MCP_PORT", "USE_MOCK_DATA", "BROBOT_CLI_JAR"]:
            monkeypatch.delenv(key, raising=False)
        
        # Create settings explicitly loading the .env file
        settings = Settings(
            _env_file=str(env_file),
            host="192.168.1.1",
            port=9000,
            use_mock_data=False,
            brobot_cli_jar="custom.jar"
        )
        
        assert settings.host == "192.168.1.1"
        assert settings.port == 9000
        assert settings.use_mock_data is False
        assert settings.brobot_cli_jar.endswith("custom.jar")


class TestGetSettings:
    """Test get_settings function."""
    
    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_get_settings_type(self):
        """Test get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)


class TestSettingsValidation:
    """Test settings validation edge cases."""
    
    def test_port_validation(self):
        """Test port number validation."""
        # Valid ports
        Settings(port=80)
        Settings(port=8080)
        Settings(port=65535)
        
        # Invalid ports should raise validation error
        with pytest.raises(Exception):  # Pydantic will validate
            Settings(port=0)
        
        with pytest.raises(Exception):
            Settings(port=70000)
    
    def test_timeout_validation(self):
        """Test timeout validation."""
        # Valid timeouts
        Settings(cli_timeout=1.0)
        Settings(cli_timeout=300.0)
        
        # Invalid timeouts
        with pytest.raises(Exception):
            Settings(cli_timeout=0.0)
        
        with pytest.raises(Exception):
            Settings(cli_timeout=-5.0)
    
    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid log levels
        for level in ["debug", "info", "warning", "error", "critical"]:
            settings = Settings(log_level=level)
            assert settings.log_level == level
    
    def test_boolean_env_parsing(self, monkeypatch):
        """Test boolean environment variable parsing."""
        # Test various boolean representations
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
        ]
        
        for env_value, expected in test_cases:
            monkeypatch.setenv("USE_MOCK_DATA", env_value)
            settings = Settings()
            assert settings.use_mock_data is expected