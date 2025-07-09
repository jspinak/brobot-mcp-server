"""Integration tests for server-CLI communication."""

import pytest
import subprocess
import json
import time
import threading
import os
from pathlib import Path
from unittest.mock import patch, Mock
import requests

from mcp_server.config import Settings
from mcp_server.brobot_bridge import initialize_bridge, get_bridge


@pytest.mark.integration
@pytest.mark.cli
class TestServerCLIIntegration:
    """Test server integration with Java CLI."""
    
    @pytest.fixture
    def server_process(self, cli_jar_path, tmp_path):
        """Start the server as a subprocess."""
        env = {
            "BROBOT_CLI_JAR": str(cli_jar_path),
            "USE_MOCK_DATA": "false",
            "MCP_PORT": "8003",
            "MCP_HOST": "127.0.0.1"
        }
        
        # Start server process
        process = subprocess.Popen(
            ["python3", "-m", "uvicorn", "mcp_server.main:app", "--port", "8003", "--host", "127.0.0.1"],
            env={**os.environ, **env},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        yield process
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
    
    @patch('subprocess.run')
    def test_state_structure_integration(self, mock_run, cli_jar_path):
        """Test getting state structure through server-CLI integration."""
        # Mock CLI response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "states": [
                {
                    "name": "main_menu",
                    "description": "Main menu",
                    "images": ["main.png"],
                    "transitions": [],
                    "isInitial": True,
                    "isFinal": False
                }
            ],
            "currentState": "main_menu",
            "metadata": {"version": "1.0"}
        })
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Initialize bridge
        initialize_bridge(str(cli_jar_path))
        bridge = get_bridge()
        
        # Test getting state structure
        result = bridge.get_state_structure()
        
        assert result["states"][0]["name"] == "main_menu"
        assert result["currentState"] == "main_menu"
        
        # Verify CLI was called correctly
        mock_run.assert_called()
        call_args = mock_run.call_args[0][0]
        assert "java" in call_args
        assert str(cli_jar_path) in call_args
        assert "get-state-structure" in call_args
    
    @patch('subprocess.run')
    def test_observation_integration(self, mock_run, cli_jar_path):
        """Test getting observation through server-CLI integration."""
        # Mock CLI response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "timestamp": "2024-01-20T10:30:00",
            "activeStates": [
                {
                    "name": "dashboard",
                    "confidence": 0.95,
                    "matchedPatterns": ["dashboard.png"]
                }
            ],
            "screenshot": "base64imagedata",
            "screenWidth": 1920,
            "screenHeight": 1080,
            "metadata": {"captureTime": 0.1}
        })
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Initialize bridge
        initialize_bridge(str(cli_jar_path))
        bridge = get_bridge()
        
        # Test getting observation
        result = bridge.get_observation()
        
        assert result["activeStates"][0]["name"] == "dashboard"
        assert result["screenshot"] == "base64imagedata"
    
    @patch('subprocess.run')
    def test_execute_action_integration(self, mock_run, cli_jar_path):
        """Test executing action through server-CLI integration."""
        # Mock CLI response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "success": True,
            "actionType": "click",
            "duration": 0.5,
            "resultState": "next_screen",
            "error": None,
            "metadata": {"clicked": True}
        })
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Initialize bridge
        initialize_bridge(str(cli_jar_path))
        bridge = get_bridge()
        
        # Test executing action
        action_request = {
            "action_type": "click",
            "parameters": {"image_pattern": "button.png"},
            "timeout": 5.0
        }
        
        result = bridge.execute_action(action_request)
        
        assert result["success"] is True
        assert result["actionType"] == "click"
        assert result["resultState"] == "next_screen"
    
    @patch('subprocess.run')
    def test_cli_error_handling(self, mock_run, cli_jar_path):
        """Test error handling in server-CLI communication."""
        # Mock CLI error
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Pattern not found: button.png"
        mock_run.return_value = mock_result
        
        # Initialize bridge
        initialize_bridge(str(cli_jar_path))
        bridge = get_bridge()
        
        # Test command that fails
        result = bridge._run_command(["execute-action", "{}"])
        
        assert result["success"] is False
        assert result["error"] == "Pattern not found: button.png"
    
    @patch('subprocess.run')
    def test_cli_timeout_handling(self, mock_run, cli_jar_path):
        """Test timeout handling in server-CLI communication."""
        # First mock successful version check
        version_result = Mock()
        version_result.stdout = "Brobot CLI v1.0.0"
        version_result.returncode = 0
        
        # Then mock timeout for actual command
        mock_run.side_effect = [
            version_result,  # For --version during initialization
            subprocess.TimeoutExpired(
                cmd=["java", "-jar", str(cli_jar_path), "slow-command"],
                timeout=5.0
            )
        ]
        
        # Initialize bridge
        initialize_bridge(str(cli_jar_path))
        bridge = get_bridge()
        
        # Test command that times out
        from mcp_server.brobot_bridge import BrobotCLIError
        with pytest.raises(BrobotCLIError) as exc_info:
            bridge._run_command(["slow-command"], timeout=5.0)
        
        assert "timed out" in str(exc_info.value)


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @patch('subprocess.run')
    def test_complete_automation_workflow(self, mock_run, cli_jar_path):
        """Test a complete automation workflow."""
        # Setup mock responses for workflow
        responses = {
            "get-state-structure": {
                "states": [
                    {"name": "login", "isInitial": True},
                    {"name": "dashboard", "isFinal": False}
                ],
                "currentState": "login"
            },
            "get-observation": {
                "activeStates": [{"name": "login", "confidence": 0.9}],
                "screenshot": "base64data"
            },
            "execute-action": {
                "success": True,
                "resultState": "dashboard"
            }
        }
        
        def mock_run_impl(*args, **kwargs):
            cmd = args[0]
            mock_result = Mock()
            
            for key, response in responses.items():
                if key in cmd:
                    mock_result.returncode = 0
                    mock_result.stdout = json.dumps(response)
                    mock_result.stderr = ""
                    return mock_result
            
            # Default response
            mock_result.returncode = 0
            mock_result.stdout = "{}"
            mock_result.stderr = ""
            return mock_result
        
        mock_run.side_effect = mock_run_impl
        
        # Initialize bridge
        initialize_bridge(str(cli_jar_path))
        bridge = get_bridge()
        
        # Execute workflow
        # 1. Get initial state
        state_structure = bridge.get_state_structure()
        assert state_structure["currentState"] == "login"
        
        # 2. Get observation
        observation = bridge.get_observation()
        assert observation["activeStates"][0]["name"] == "login"
        
        # 3. Execute action to transition
        action = {
            "action_type": "click",
            "parameters": {"image_pattern": "login_button.png"}
        }
        result = bridge.execute_action(action)
        assert result["success"] is True
        assert result["resultState"] == "dashboard"


@pytest.mark.integration
@pytest.mark.slow
class TestServerAPIIntegration:
    """Test server API with CLI integration."""
    
    @pytest.mark.skipif(not Path("brobot-cli/build/libs/brobot-cli.jar").exists(),
                        reason="Requires built brobot-cli.jar")
    def test_api_with_real_cli(self):
        """Test API endpoints with real CLI (if available)."""
        # This test would only run if the real CLI is built
        import requests
        
        # Start server with real CLI
        base_url = "http://localhost:8000"
        
        # Test state structure endpoint
        response = requests.get(f"{base_url}/api/v1/state_structure")
        assert response.status_code == 200
        data = response.json()
        assert "states" in data
        
        # Test observation endpoint
        response = requests.get(f"{base_url}/api/v1/observation")
        assert response.status_code == 200
        data = response.json()
        assert "active_states" in data
        assert "screenshot" in data
        
        # Test execute endpoint
        action_request = {
            "action_type": "wait",
            "parameters": {"duration": 1.0}
        }
        response = requests.post(f"{base_url}/api/v1/execute", json=action_request)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data