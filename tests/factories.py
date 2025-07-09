"""Test factories for creating mock objects."""

from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from pathlib import Path

from mcp_server.config import Settings
from mcp_server.brobot_bridge import CLIConfig, BrobotBridge
from tests.utils import MockDataGenerator


class SettingsFactory:
    """Factory for creating Settings instances."""
    
    @staticmethod
    def create(
        host: str = "127.0.0.1",
        port: int = 8000,
        use_mock_data: bool = True,
        brobot_cli_jar: Optional[str] = None,
        **kwargs
    ) -> Settings:
        """Create a Settings instance with sensible defaults."""
        settings_dict = {
            "host": host,
            "port": port,
            "use_mock_data": use_mock_data,
            "brobot_cli_jar": brobot_cli_jar,
            "reload": False,
            "log_level": "info",
            "java_executable": "java",
            "cli_timeout": 30.0,
            "api_version": "v1"
        }
        settings_dict.update(kwargs)
        
        return Settings(**settings_dict)
    
    @staticmethod
    def create_mock_settings(is_cli_configured: bool = False) -> Mock:
        """Create a mock Settings instance."""
        mock_settings = Mock(spec=Settings)
        mock_settings.host = "127.0.0.1"
        mock_settings.port = 8000
        mock_settings.use_mock_data = not is_cli_configured
        mock_settings.brobot_cli_jar = "/path/to/cli.jar" if is_cli_configured else None
        mock_settings.is_cli_configured = is_cli_configured
        mock_settings.java_executable = "java"
        mock_settings.cli_timeout = 30.0
        mock_settings.api_version = "v1"
        mock_settings.log_level = "info"
        
        return mock_settings


class BridgeFactory:
    """Factory for creating BrobotBridge instances."""
    
    @staticmethod
    def create_mock_bridge(
        available: bool = True,
        state_structure: Optional[Dict[str, Any]] = None,
        observation: Optional[Dict[str, Any]] = None
    ) -> Mock:
        """Create a mock BrobotBridge instance."""
        mock_bridge = Mock(spec=BrobotBridge)
        
        # Configure is_available
        mock_bridge.is_available.return_value = available
        
        # Configure get_state_structure
        if state_structure is None:
            state_structure = MockDataGenerator.generate_state_structure()
        mock_bridge.get_state_structure.return_value = state_structure
        
        # Configure get_observation
        if observation is None:
            observation = MockDataGenerator.generate_observation()
        mock_bridge.get_observation.return_value = observation
        
        # Configure execute_action
        def execute_action_impl(request):
            action_type = request.get("action_type", "unknown")
            return MockDataGenerator.generate_action_result(True, action_type)
        
        mock_bridge.execute_action.side_effect = execute_action_impl
        
        # Configure _run_command for low-level testing
        def run_command_impl(args, timeout=None):
            command = args[0] if args else ""
            
            if command == "get-state-structure":
                return {
                    "success": True,
                    "output": json.dumps(state_structure),
                    "error": None
                }
            elif command == "get-observation":
                return {
                    "success": True,
                    "output": json.dumps(observation),
                    "error": None
                }
            else:
                return {
                    "success": True,
                    "output": "{}",
                    "error": None
                }
        
        mock_bridge._run_command.side_effect = run_command_impl
        
        return mock_bridge


class ResponseFactory:
    """Factory for creating HTTP responses."""
    
    @staticmethod
    def create_mock_response(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = "",
        raise_for_status: bool = False
    ) -> Mock:
        """Create a mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = text
        
        if json_data is not None:
            mock_response.json.return_value = json_data
        else:
            mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        
        if raise_for_status and status_code >= 400:
            import requests
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        else:
            mock_response.raise_for_status.return_value = None
        
        return mock_response
    
    @staticmethod
    def create_async_mock_response(
        status: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = ""
    ) -> AsyncMock:
        """Create an async mock HTTP response."""
        mock_response = AsyncMock()
        mock_response.status = status
        mock_response.text = AsyncMock(return_value=text)
        
        if json_data is not None:
            mock_response.json = AsyncMock(return_value=json_data)
        else:
            mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid", "", 0))
        
        if status >= 400:
            import aiohttp
            mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
                request_info=Mock(),
                history=(),
                status=status
            )
        else:
            mock_response.raise_for_status = AsyncMock()
        
        return mock_response


class SubprocessFactory:
    """Factory for creating subprocess mocks."""
    
    @staticmethod
    def create_mock_result(
        returncode: int = 0,
        stdout: str = "",
        stderr: str = ""
    ) -> Mock:
        """Create a mock subprocess result."""
        mock_result = Mock()
        mock_result.returncode = returncode
        mock_result.stdout = stdout
        mock_result.stderr = stderr
        return mock_result
    
    @staticmethod
    def create_mock_run(responses: Dict[str, Dict[str, Any]]) -> Mock:
        """Create a mock subprocess.run that returns different results based on command."""
        def run_impl(cmd, *args, **kwargs):
            # Extract the relevant command part
            command_key = None
            for part in cmd:
                if part in responses:
                    command_key = part
                    break
            
            if command_key and command_key in responses:
                response = responses[command_key]
                return SubprocessFactory.create_mock_result(**response)
            
            # Default response
            return SubprocessFactory.create_mock_result(
                returncode=0,
                stdout="{}",
                stderr=""
            )
        
        mock_run = Mock()
        mock_run.side_effect = run_impl
        return mock_run


class ClientFactory:
    """Factory for creating client mocks."""
    
    @staticmethod
    def create_mock_session() -> Mock:
        """Create a mock requests Session."""
        mock_session = Mock()
        
        # Default successful responses
        mock_session.get.return_value = ResponseFactory.create_mock_response(
            json_data={"status": "ok"}
        )
        mock_session.post.return_value = ResponseFactory.create_mock_response(
            json_data={"success": True}
        )
        
        return mock_session
    
    @staticmethod
    def create_async_mock_session() -> AsyncMock:
        """Create a mock aiohttp ClientSession."""
        mock_session = AsyncMock()
        
        # Create context managers for HTTP methods
        async def create_context_manager(response):
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = response
            mock_cm.__aexit__.return_value = None
            return mock_cm
        
        # Default successful responses
        mock_session.get.return_value = create_context_manager(
            ResponseFactory.create_async_mock_response(
                json_data={"status": "ok"}
            )
        )
        mock_session.post.return_value = create_context_manager(
            ResponseFactory.create_async_mock_response(
                json_data={"success": True}
            )
        )
        
        mock_session.closed = False
        mock_session.close = AsyncMock()
        
        return mock_session


class FixtureFactory:
    """Factory for creating test fixtures."""
    
    @staticmethod
    def create_test_environment(tmp_path: Path) -> Dict[str, Any]:
        """Create a complete test environment."""
        # Create directory structure
        jar_dir = tmp_path / "brobot-cli" / "build" / "libs"
        jar_dir.mkdir(parents=True)
        
        # Create mock JAR
        jar_path = jar_dir / "brobot-cli.jar"
        jar_path.write_bytes(b"PK\x03\x04")
        
        # Create .env file
        env_path = tmp_path / ".env"
        env_content = f"""
BROBOT_CLI_JAR={jar_path}
USE_MOCK_DATA=false
MCP_PORT=8001
"""
        env_path.write_text(env_content)
        
        # Create test images
        images_dir = tmp_path / "test_images"
        images_dir.mkdir()
        
        test_images = {}
        for name in ["button.png", "logo.png", "menu.png"]:
            img_path = images_dir / name
            img_path.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
            test_images[name] = img_path
        
        return {
            "root": tmp_path,
            "jar_path": jar_path,
            "env_path": env_path,
            "images_dir": images_dir,
            "test_images": test_images
        }