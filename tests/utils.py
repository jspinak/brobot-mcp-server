"""Test utilities and helper functions."""

import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import random
import string


class MockDataGenerator:
    """Generate realistic mock data for testing."""
    
    @staticmethod
    def generate_state(name: str = None, is_initial: bool = False, is_final: bool = False) -> Dict[str, Any]:
        """Generate a mock state."""
        if name is None:
            name = f"state_{MockDataGenerator.random_string(6)}"
        
        return {
            "name": name,
            "description": f"Description for {name}",
            "images": [f"{name}_{i}.png" for i in range(random.randint(1, 3))],
            "transitions": MockDataGenerator.generate_transitions(name),
            "isInitial": is_initial,
            "isFinal": is_final
        }
    
    @staticmethod
    def generate_transitions(from_state: str, count: int = None) -> List[Dict[str, Any]]:
        """Generate mock state transitions."""
        if count is None:
            count = random.randint(0, 3)
        
        transitions = []
        for i in range(count):
            transitions.append({
                "fromState": from_state,
                "toState": f"state_{MockDataGenerator.random_string(6)}",
                "action": random.choice(["click", "type", "drag", "wait"]),
                "probability": round(random.uniform(0.7, 0.99), 2)
            })
        
        return transitions
    
    @staticmethod
    def generate_state_structure(num_states: int = 3) -> Dict[str, Any]:
        """Generate a complete state structure."""
        states = []
        
        # Generate initial state
        states.append(MockDataGenerator.generate_state("initial_state", is_initial=True))
        
        # Generate intermediate states
        for i in range(num_states - 2):
            states.append(MockDataGenerator.generate_state())
        
        # Generate final state
        if num_states > 1:
            states.append(MockDataGenerator.generate_state("final_state", is_final=True))
        
        return {
            "states": states,
            "currentState": states[0]["name"],
            "metadata": {
                "version": "1.0.0",
                "generated": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def generate_observation() -> Dict[str, Any]:
        """Generate a mock observation."""
        active_states = []
        num_states = random.randint(1, 3)
        
        for i in range(num_states):
            active_states.append({
                "name": f"state_{MockDataGenerator.random_string(6)}",
                "confidence": round(random.uniform(0.6, 0.99), 2),
                "matchedPatterns": [f"pattern_{j}.png" for j in range(random.randint(1, 3))]
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "activeStates": active_states,
            "screenshot": MockDataGenerator.generate_screenshot(),
            "screenWidth": 1920,
            "screenHeight": 1080,
            "metadata": {
                "captureDuration": round(random.uniform(0.05, 0.2), 3),
                "analysisDuration": round(random.uniform(0.01, 0.1), 3)
            }
        }
    
    @staticmethod
    def generate_screenshot() -> str:
        """Generate a base64 encoded mock screenshot."""
        # Simple 1x1 PNG
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\xf8\n\xf0d\x00\x00\x00\x00IEND\xaeB`\x82'
        return base64.b64encode(png_data).decode('utf-8')
    
    @staticmethod
    def generate_action_result(success: bool = True, action_type: str = "click") -> Dict[str, Any]:
        """Generate a mock action result."""
        return {
            "success": success,
            "actionType": action_type,
            "duration": round(random.uniform(0.1, 2.0), 3),
            "resultState": f"state_{MockDataGenerator.random_string(6)}" if success else None,
            "error": None if success else "Action failed: Pattern not found",
            "metadata": {
                "attemptCount": 1,
                "confidence": round(random.uniform(0.8, 0.99), 2) if success else 0.0
            }
        }
    
    @staticmethod
    def random_string(length: int = 8) -> str:
        """Generate a random string."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class TestFileHelper:
    """Helper for creating and managing test files."""
    
    @staticmethod
    def create_mock_jar(path: Path) -> Path:
        """Create a mock JAR file for testing."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"PK\x03\x04")  # JAR file signature
        return path
    
    @staticmethod
    def create_test_image(path: Path, width: int = 100, height: int = 100) -> Path:
        """Create a test PNG image."""
        path.parent.mkdir(parents=True, exist_ok=True)
        # Create a simple PNG header (this is not a valid image but has correct signature)
        png_header = b'\x89PNG\r\n\x1a\n'
        path.write_bytes(png_header + b'\x00' * 100)
        return path
    
    @staticmethod
    def create_env_file(path: Path, config: Dict[str, str]) -> Path:
        """Create a .env file with given configuration."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = []
        for key, value in config.items():
            lines.append(f"{key}={value}")
        
        path.write_text('\n'.join(lines))
        return path


class APITestHelper:
    """Helper for API testing."""
    
    @staticmethod
    def assert_valid_state_structure(data: Dict[str, Any]):
        """Assert that data is a valid state structure."""
        assert "states" in data
        assert isinstance(data["states"], list)
        assert len(data["states"]) > 0
        
        for state in data["states"]:
            assert "name" in state
            assert isinstance(state["name"], str)
            
        assert "current_state" in data or "currentState" in data
        assert "metadata" in data
    
    @staticmethod
    def assert_valid_observation(data: Dict[str, Any]):
        """Assert that data is a valid observation."""
        assert "timestamp" in data
        assert "active_states" in data or "activeStates" in data
        
        states_key = "active_states" if "active_states" in data else "activeStates"
        assert isinstance(data[states_key], list)
        
        for state in data[states_key]:
            assert "name" in state
            assert "confidence" in state
            assert 0.0 <= state["confidence"] <= 1.0
        
        assert "screenshot" in data
        assert "screen_width" in data or "screenWidth" in data
        assert "screen_height" in data or "screenHeight" in data
    
    @staticmethod
    def assert_valid_action_result(data: Dict[str, Any]):
        """Assert that data is a valid action result."""
        assert "success" in data
        assert isinstance(data["success"], bool)
        assert "action_type" in data or "actionType" in data
        
        if data["success"]:
            assert "duration" in data
            assert data["duration"] >= 0
        else:
            assert "error" in data
            assert data["error"] is not None


class AsyncTestHelper:
    """Helper for async testing."""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
        """Wait for a condition to become true."""
        import asyncio
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False
    
    @staticmethod
    async def gather_with_timeout(coros: List, timeout: float = 10.0):
        """Gather multiple coroutines with a timeout."""
        import asyncio
        
        try:
            return await asyncio.wait_for(
                asyncio.gather(*coros),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None


def assert_json_equal(actual: Any, expected: Any, ignore_keys: Optional[List[str]] = None):
    """Assert two JSON-like structures are equal, optionally ignoring certain keys."""
    if ignore_keys is None:
        ignore_keys = []
    
    if isinstance(actual, dict) and isinstance(expected, dict):
        # Check keys match (excluding ignored keys)
        actual_keys = set(actual.keys()) - set(ignore_keys)
        expected_keys = set(expected.keys()) - set(ignore_keys)
        assert actual_keys == expected_keys, f"Keys mismatch: {actual_keys} != {expected_keys}"
        
        # Recursively check values
        for key in actual_keys:
            assert_json_equal(actual[key], expected[key], ignore_keys)
    
    elif isinstance(actual, list) and isinstance(expected, list):
        assert len(actual) == len(expected), f"List length mismatch: {len(actual)} != {len(expected)}"
        for a, e in zip(actual, expected):
            assert_json_equal(a, e, ignore_keys)
    
    else:
        assert actual == expected, f"Value mismatch: {actual} != {expected}"


def create_mock_cli_response(command: str, success: bool = True) -> Dict[str, Any]:
    """Create a mock CLI response for a given command."""
    if command == "get-state-structure":
        return {
            "success": success,
            "output": json.dumps(MockDataGenerator.generate_state_structure()) if success else "",
            "error": None if success else "CLI error"
        }
    
    elif command == "get-observation":
        return {
            "success": success,
            "output": json.dumps(MockDataGenerator.generate_observation()) if success else "",
            "error": None if success else "CLI error"
        }
    
    elif command == "execute-action":
        return {
            "success": success,
            "output": json.dumps(MockDataGenerator.generate_action_result(success)) if success else "",
            "error": None if success else "CLI error"
        }
    
    else:
        return {
            "success": False,
            "output": "",
            "error": f"Unknown command: {command}"
        }