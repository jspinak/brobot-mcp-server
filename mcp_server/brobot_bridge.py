"""Bridge module for communicating with the Brobot CLI."""

import subprocess
import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BrobotCommand(Enum):
    """Available Brobot CLI commands."""
    GET_STATE_STRUCTURE = "get-state-structure"
    GET_OBSERVATION = "get-observation"
    EXECUTE_ACTION = "execute-action"


class BrobotCLIError(Exception):
    """Exception raised when Brobot CLI encounters an error."""
    pass


@dataclass
class CLIConfig:
    """Configuration for the Brobot CLI."""
    jar_path: Path
    java_executable: str = "java"
    default_timeout: float = 30.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.jar_path = Path(self.jar_path)
        if not self.jar_path.exists():
            raise FileNotFoundError(f"Brobot CLI JAR not found at: {self.jar_path}")


class BrobotBridge:
    """Bridge for communicating with the Brobot CLI via subprocess."""
    
    def __init__(self, config: CLIConfig):
        """
        Initialize the Brobot bridge.
        
        Args:
            config: CLI configuration
        """
        self.config = config
        self._validate_cli()
    
    def _validate_cli(self) -> None:
        """Validate that the CLI is accessible and working."""
        try:
            result = self._run_command(["--version"], timeout=5.0)
            logger.info(f"Brobot CLI validated: {result.get('output', '').strip()}")
        except Exception as e:
            raise BrobotCLIError(f"Failed to validate Brobot CLI: {e}")
    
    def _run_command(self, args: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Run a CLI command and return the result.
        
        Args:
            args: Command arguments
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with 'success', 'output', and 'error' keys
        """
        if timeout is None:
            timeout = self.config.default_timeout
            
        cmd = [self.config.java_executable, "-jar", str(self.config.jar_path)] + args
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "output": result.stdout,
                    "error": result.stderr or f"Command failed with code {result.returncode}"
                }
                
        except subprocess.TimeoutExpired:
            raise BrobotCLIError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise BrobotCLIError(f"Failed to run command: {e}")
    
    def get_state_structure(self) -> Dict[str, Any]:
        """
        Get the application state structure.
        
        Returns:
            State structure as a dictionary
        """
        result = self._run_command([BrobotCommand.GET_STATE_STRUCTURE.value])
        
        if not result["success"]:
            raise BrobotCLIError(f"Failed to get state structure: {result['error']}")
        
        try:
            return json.loads(result["output"])
        except json.JSONDecodeError as e:
            raise BrobotCLIError(f"Invalid JSON response from CLI: {e}")
    
    def get_observation(self) -> Dict[str, Any]:
        """
        Get current observation of the application.
        
        Returns:
            Observation data as a dictionary
        """
        result = self._run_command([BrobotCommand.GET_OBSERVATION.value])
        
        if not result["success"]:
            raise BrobotCLIError(f"Failed to get observation: {result['error']}")
        
        try:
            return json.loads(result["output"])
        except json.JSONDecodeError as e:
            raise BrobotCLIError(f"Invalid JSON response from CLI: {e}")
    
    def execute_action(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an automation action.
        
        Args:
            action_request: Action request dictionary
            
        Returns:
            Action result as a dictionary
        """
        # Convert action request to JSON
        json_payload = json.dumps(action_request)
        
        # Use custom timeout if specified in request
        timeout = action_request.get("timeout", self.config.default_timeout)
        
        result = self._run_command(
            [BrobotCommand.EXECUTE_ACTION.value, json_payload],
            timeout=timeout
        )
        
        if not result["success"]:
            raise BrobotCLIError(f"Failed to execute action: {result['error']}")
        
        try:
            return json.loads(result["output"])
        except json.JSONDecodeError as e:
            raise BrobotCLIError(f"Invalid JSON response from CLI: {e}")
    
    def is_available(self) -> bool:
        """
        Check if the Brobot CLI is available.
        
        Returns:
            True if CLI is available, False otherwise
        """
        try:
            result = self._run_command(["--help"], timeout=5.0)
            return result["success"]
        except:
            return False


# Global bridge instance (will be initialized by the app)
_bridge: Optional[BrobotBridge] = None


def initialize_bridge(jar_path: str, java_executable: str = "java") -> None:
    """
    Initialize the global Brobot bridge.
    
    Args:
        jar_path: Path to the Brobot CLI JAR
        java_executable: Java executable path (default: "java")
    """
    global _bridge
    config = CLIConfig(jar_path=jar_path, java_executable=java_executable)
    _bridge = BrobotBridge(config)
    logger.info(f"Brobot bridge initialized with JAR at: {jar_path}")


def get_bridge() -> BrobotBridge:
    """
    Get the global Brobot bridge instance.
    
    Returns:
        The bridge instance
        
    Raises:
        RuntimeError: If bridge is not initialized
    """
    if _bridge is None:
        raise RuntimeError("Brobot bridge not initialized. Call initialize_bridge() first.")
    return _bridge