"""Shared pytest fixtures and configuration."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock
import json
import base64
import asyncio

from fastapi.testclient import TestClient
from mcp_server.main import app
from mcp_server.config import Settings
from mcp_server.brobot_bridge import BrobotBridge, CLIConfig
# Temporarily skip client imports for testing
try:
    from brobot_client import BrobotClient, AsyncBrobotClient
except ImportError:
    BrobotClient = None
    AsyncBrobotClient = None


# Test data fixtures
@pytest.fixture
def mock_state_structure():
    """Mock state structure data."""
    return {
        "states": [
            {
                "name": "main_menu",
                "description": "Main application menu",
                "images": ["main_menu.png", "logo.png"],
                "transitions": [
                    {
                        "fromState": "main_menu",
                        "toState": "login",
                        "action": "click_login",
                        "probability": 0.95
                    }
                ],
                "isInitial": True,
                "isFinal": False
            },
            {
                "name": "login",
                "description": "Login screen",
                "images": ["login_form.png"],
                "transitions": [
                    {
                        "fromState": "login",
                        "toState": "dashboard",
                        "action": "submit_credentials",
                        "probability": 0.90
                    }
                ],
                "isInitial": False,
                "isFinal": False
            }
        ],
        "currentState": "main_menu",
        "metadata": {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    }


@pytest.fixture
def mock_observation():
    """Mock observation data."""
    # Create a small test image
    test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\xf8\n\xf0d\x00\x00\x00\x00IEND\xaeB`\x82'
    
    return {
        "timestamp": datetime.now().isoformat(),
        "activeStates": [
            {
                "name": "main_menu",
                "confidence": 0.95,
                "matchedPatterns": ["main_menu.png", "logo.png"]
            },
            {
                "name": "notification",
                "confidence": 0.72,
                "matchedPatterns": ["notification_icon.png"]
            }
        ],
        "screenshot": base64.b64encode(test_image).decode('utf-8'),
        "screenWidth": 1920,
        "screenHeight": 1080,
        "metadata": {
            "captureDuration": 0.125,
            "analysisDuration": 0.087
        }
    }


@pytest.fixture
def mock_action_result():
    """Mock action result data."""
    return {
        "success": True,
        "actionType": "click",
        "duration": 0.523,
        "resultState": "login",
        "error": None,
        "metadata": {
            "clickLocation": {"x": 640, "y": 480},
            "patternFound": True,
            "confidence": 0.92
        }
    }


# Configuration fixtures
@pytest.fixture
def test_settings(tmp_path):
    """Test settings with temporary paths."""
    return Settings(
        use_mock_data=True,
        brobot_cli_jar=str(tmp_path / "test-cli.jar"),
        java_executable="java",
        cli_timeout=5.0,
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="debug"
    )


@pytest.fixture
def mock_cli_config(tmp_path):
    """Mock CLI configuration."""
    # Create a fake JAR file
    jar_path = tmp_path / "brobot-cli.jar"
    jar_path.write_text("mock jar content")
    
    return CLIConfig(
        jar_path=jar_path,
        java_executable="java",
        default_timeout=5.0
    )


# Bridge and client fixtures
@pytest.fixture
def mock_bridge(mock_cli_config, monkeypatch):
    """Mock Brobot bridge."""
    bridge = BrobotBridge(mock_cli_config)
    
    # Mock the _run_command method
    def mock_run_command(args, timeout=None):
        if "--version" in args:
            return {"success": True, "output": "brobot-cli 0.1.0", "error": None}
        elif "get-state-structure" in args:
            return {"success": True, "output": json.dumps({"states": []}), "error": None}
        else:
            return {"success": True, "output": "{}", "error": None}
    
    monkeypatch.setattr(bridge, "_run_command", mock_run_command)
    return bridge


@pytest.fixture
def test_client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def client_with_mock_server(test_client):
    """Brobot client configured for test server."""
    if BrobotClient is None:
        pytest.skip("BrobotClient not available")
    return BrobotClient(base_url="http://testserver")


@pytest.fixture
async def async_client_with_mock_server():
    """Async Brobot client for testing."""
    if AsyncBrobotClient is None:
        pytest.skip("AsyncBrobotClient not available")
    client = AsyncBrobotClient(base_url="http://testserver")
    yield client
    await client.close()


# Mock subprocess fixtures
@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run for CLI tests."""
    def mock_run(*args, **kwargs):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"success": true}'
        mock_result.stderr = ""
        return mock_result
    
    monkeypatch.setattr("subprocess.run", mock_run)
    return mock_run


# Temporary file fixtures
@pytest.fixture
def temp_image_file(tmp_path):
    """Create a temporary image file."""
    image_path = tmp_path / "test_pattern.png"
    # Write minimal PNG data
    image_path.write_bytes(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f'
        b'\x00\x00\x01\x01\x00\x05\xf8\n\xf0d\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return image_path


@pytest.fixture
def temp_env_file(tmp_path, monkeypatch):
    """Create temporary .env file."""
    env_path = tmp_path / ".env"
    env_content = """
USE_MOCK_DATA=true
MCP_PORT=8002
BROBOT_CLI_JAR=test.jar
"""
    env_path.write_text(env_content)
    
    # Change to temp directory
    monkeypatch.chdir(tmp_path)
    
    return env_path


# Async fixtures
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield


# Integration test fixtures
@pytest.fixture
def test_server():
    """Run test server in a thread for integration tests."""
    import uvicorn
    import threading
    import time
    
    server = uvicorn.Server(
        uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8004,
            log_level="error"
        )
    )
    
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    
    # Wait for server to start
    time.sleep(1)
    
    yield "http://127.0.0.1:8004"
    
    # Server will stop when thread ends


@pytest.fixture
def cli_jar_path(tmp_path):
    """Create a mock CLI JAR for testing."""
    # In real tests, this would point to actual brobot-cli.jar
    jar_path = tmp_path / "brobot-cli.jar"
    jar_path.write_text("mock jar")
    return jar_path
    # Add any cleanup code here
    

# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "cli: mark test as requiring Java CLI"
    )
    config.addinivalue_line(
        "markers", "mock: mark test as using mock data"
    )