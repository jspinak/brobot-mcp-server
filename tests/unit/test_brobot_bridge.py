"""Unit tests for brobot_bridge module."""

import pytest
import subprocess
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from mcp_server.brobot_bridge import (
    BrobotCommand,
    BrobotCLIError,
    CLIConfig,
    BrobotBridge,
    initialize_bridge,
    get_bridge
)


class TestBrobotCommand:
    """Test BrobotCommand enum."""
    
    def test_command_values(self):
        """Test command enum values."""
        assert BrobotCommand.GET_STATE_STRUCTURE.value == "get-state-structure"
        assert BrobotCommand.GET_OBSERVATION.value == "get-observation"
        assert BrobotCommand.EXECUTE_ACTION.value == "execute-action"


class TestCLIConfig:
    """Test CLIConfig dataclass."""
    
    def test_cli_config_creation(self, tmp_path):
        """Test CLIConfig creation with valid JAR."""
        jar_path = tmp_path / "test.jar"
        jar_path.write_text("mock jar")
        
        config = CLIConfig(
            jar_path=jar_path,
            java_executable="java",
            default_timeout=30.0
        )
        
        assert config.jar_path == jar_path
        assert config.java_executable == "java"
        assert config.default_timeout == 30.0
    
    def test_cli_config_path_conversion(self, tmp_path):
        """Test CLIConfig converts string path to Path."""
        jar_path = tmp_path / "test.jar"
        jar_path.write_text("mock jar")
        
        # Pass as string
        config = CLIConfig(jar_path=str(jar_path))
        
        assert isinstance(config.jar_path, Path)
        assert config.jar_path == jar_path
    
    def test_cli_config_missing_jar(self):
        """Test CLIConfig with missing JAR file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            CLIConfig(jar_path="/nonexistent/path.jar")
        
        assert "Brobot CLI JAR not found" in str(exc_info.value)
    
    def test_cli_config_defaults(self, tmp_path):
        """Test CLIConfig default values."""
        jar_path = tmp_path / "test.jar"
        jar_path.write_text("mock jar")
        
        config = CLIConfig(jar_path=jar_path)
        
        assert config.java_executable == "java"
        assert config.default_timeout == 30.0


class TestBrobotBridge:
    """Test BrobotBridge class."""
    
    @patch('subprocess.run')
    def test_bridge_initialization(self, mock_run, tmp_path):
        """Test BrobotBridge initialization."""
        # Setup
        jar_path = tmp_path / "test.jar"
        jar_path.write_text("mock jar")
        config = CLIConfig(jar_path=jar_path)
        
        # Mock subprocess for validation
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "brobot-cli 0.1.0"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Create bridge
        bridge = BrobotBridge(config)
        
        assert bridge.config == config
        # Verify validation was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "java" in call_args
        assert str(jar_path) in call_args
        assert "--version" in call_args
    
    @patch('subprocess.run')
    def test_bridge_initialization_failure(self, mock_run, tmp_path):
        """Test BrobotBridge initialization with CLI failure."""
        # Setup
        jar_path = tmp_path / "test.jar"
        jar_path.write_text("mock jar")
        config = CLIConfig(jar_path=jar_path)
        
        # Mock subprocess failure
        mock_run.side_effect = Exception("Java not found")
        
        # Should raise error
        with pytest.raises(BrobotCLIError) as exc_info:
            BrobotBridge(config)
        
        assert "Failed to validate Brobot CLI" in str(exc_info.value)
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run, mock_bridge):
        """Test _run_command with successful execution."""
        # Mock successful subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true}'
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Restore original _run_command
        bridge = mock_bridge
        bridge._run_command = BrobotBridge._run_command.__get__(bridge)
        
        result = bridge._run_command(["test-command"])
        
        assert result["success"] is True
        assert result["output"] == '{"success": true}'
        assert result["error"] is None
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run, mock_bridge):
        """Test _run_command with failed execution."""
        # Mock failed subprocess
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_run.return_value = mock_result
        
        # Restore original _run_command
        bridge = mock_bridge
        bridge._run_command = BrobotBridge._run_command.__get__(bridge)
        
        result = bridge._run_command(["failing-command"])
        
        assert result["success"] is False
        assert result["error"] == "Command failed"
    
    @patch('subprocess.run')
    def test_run_command_timeout(self, mock_run, mock_bridge):
        """Test _run_command with timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["java", "-jar", "test.jar"],
            timeout=5.0
        )
        
        # Restore original _run_command
        bridge = mock_bridge
        bridge._run_command = BrobotBridge._run_command.__get__(bridge)
        
        with pytest.raises(BrobotCLIError) as exc_info:
            bridge._run_command(["slow-command"], timeout=5.0)
        
        assert "Command timed out after 5.0 seconds" in str(exc_info.value)
    
    def test_get_state_structure(self, mock_bridge):
        """Test get_state_structure method."""
        # Mock successful response
        mock_data = {
            "states": [{"name": "test_state"}],
            "currentState": "test_state"
        }
        
        mock_bridge._run_command = Mock(return_value={
            "success": True,
            "output": json.dumps(mock_data),
            "error": None
        })
        
        result = mock_bridge.get_state_structure()
        
        assert result == mock_data
        mock_bridge._run_command.assert_called_once_with(["get-state-structure"])
    
    def test_get_state_structure_failure(self, mock_bridge):
        """Test get_state_structure with CLI failure."""
        mock_bridge._run_command = Mock(return_value={
            "success": False,
            "output": "",
            "error": "CLI error"
        })
        
        with pytest.raises(BrobotCLIError) as exc_info:
            mock_bridge.get_state_structure()
        
        assert "Failed to get state structure" in str(exc_info.value)
    
    def test_get_state_structure_invalid_json(self, mock_bridge):
        """Test get_state_structure with invalid JSON response."""
        mock_bridge._run_command = Mock(return_value={
            "success": True,
            "output": "invalid json",
            "error": None
        })
        
        with pytest.raises(BrobotCLIError) as exc_info:
            mock_bridge.get_state_structure()
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    def test_get_observation(self, mock_bridge):
        """Test get_observation method."""
        mock_data = {
            "timestamp": "2024-01-20T10:30:00",
            "activeStates": [{"name": "main", "confidence": 0.9}],
            "screenshot": "base64data"
        }
        
        mock_bridge._run_command = Mock(return_value={
            "success": True,
            "output": json.dumps(mock_data),
            "error": None
        })
        
        result = mock_bridge.get_observation()
        
        assert result == mock_data
        mock_bridge._run_command.assert_called_once_with(["get-observation"])
    
    def test_execute_action(self, mock_bridge):
        """Test execute_action method."""
        action_request = {
            "action_type": "click",
            "parameters": {"image_pattern": "button.png"},
            "timeout": 5.0
        }
        
        mock_result = {
            "success": True,
            "actionType": "click",
            "duration": 0.5
        }
        
        mock_bridge._run_command = Mock(return_value={
            "success": True,
            "output": json.dumps(mock_result),
            "error": None
        })
        
        result = mock_bridge.execute_action(action_request)
        
        assert result == mock_result
        
        # Verify command was called correctly
        call_args = mock_bridge._run_command.call_args
        assert call_args[0][0] == ["execute-action", json.dumps(action_request)]
        assert call_args[1]["timeout"] == 5.0
    
    def test_execute_action_custom_timeout(self, mock_bridge):
        """Test execute_action with custom timeout."""
        action_request = {
            "action_type": "wait",
            "parameters": {"state": "loaded"},
            "timeout": 60.0
        }
        
        mock_bridge._run_command = Mock(return_value={
            "success": True,
            "output": "{}",
            "error": None
        })
        
        mock_bridge.execute_action(action_request)
        
        # Verify timeout was passed
        call_kwargs = mock_bridge._run_command.call_args[1]
        assert call_kwargs["timeout"] == 60.0
    
    def test_is_available_true(self, mock_bridge):
        """Test is_available when CLI is accessible."""
        mock_bridge._run_command = Mock(return_value={
            "success": True,
            "output": "Help text",
            "error": None
        })
        
        assert mock_bridge.is_available() is True
        mock_bridge._run_command.assert_called_once_with(["--help"], timeout=5.0)
    
    def test_is_available_false(self, mock_bridge):
        """Test is_available when CLI is not accessible."""
        mock_bridge._run_command = Mock(side_effect=Exception("CLI not found"))
        
        assert mock_bridge.is_available() is False


class TestBridgeModule:
    """Test module-level functions."""
    
    def test_initialize_bridge(self, tmp_path, monkeypatch):
        """Test initialize_bridge function."""
        # Create mock JAR
        jar_path = tmp_path / "test.jar"
        jar_path.write_text("mock jar")
        
        # Mock subprocess for validation
        mock_run = Mock()
        mock_run.return_value = Mock(returncode=0, stdout="0.1.0", stderr="")
        monkeypatch.setattr("subprocess.run", mock_run)
        
        # Initialize bridge
        initialize_bridge(str(jar_path))
        
        # Verify bridge is set
        bridge = get_bridge()
        assert bridge is not None
        assert bridge.config.jar_path == jar_path
    
    def test_get_bridge_not_initialized(self):
        """Test get_bridge when not initialized."""
        # Reset global bridge
        import mcp_server.brobot_bridge
        mcp_server.brobot_bridge._bridge = None
        
        with pytest.raises(RuntimeError) as exc_info:
            get_bridge()
        
        assert "Brobot bridge not initialized" in str(exc_info.value)
    
    def test_initialize_bridge_custom_java(self, tmp_path, monkeypatch):
        """Test initialize_bridge with custom Java executable."""
        # Create mock JAR
        jar_path = tmp_path / "test.jar"
        jar_path.write_text("mock jar")
        
        # Mock subprocess
        mock_run = Mock()
        mock_run.return_value = Mock(returncode=0, stdout="0.1.0", stderr="")
        monkeypatch.setattr("subprocess.run", mock_run)
        
        # Initialize with custom Java
        initialize_bridge(str(jar_path), java_executable="/custom/java")
        
        bridge = get_bridge()
        assert bridge.config.java_executable == "/custom/java"


class TestBrobotCLIError:
    """Test BrobotCLIError exception."""
    
    def test_cli_error_creation(self):
        """Test BrobotCLIError creation."""
        error = BrobotCLIError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)