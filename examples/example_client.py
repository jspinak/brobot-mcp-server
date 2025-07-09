#!/usr/bin/env python3
"""Example client demonstrating how to interact with the Brobot MCP Server API."""

import requests
import json
import base64
from typing import Dict, Any, List


class BrobotMCPClient:
    """Simple client for interacting with the Brobot MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def get_state_structure(self) -> Dict[str, Any]:
        """Get the application state structure."""
        response = requests.get(f"{self.api_base}/state_structure")
        response.raise_for_status()
        return response.json()
    
    def get_observation(self) -> Dict[str, Any]:
        """Get current observation of the application."""
        response = requests.get(f"{self.api_base}/observation")
        response.raise_for_status()
        return response.json()
    
    def execute_action(self, action_type: str, parameters: Dict[str, Any], 
                      target_state: str = None, timeout: float = 10.0) -> Dict[str, Any]:
        """Execute an automation action."""
        payload = {
            "action_type": action_type,
            "parameters": parameters,
            "timeout": timeout
        }
        if target_state:
            payload["target_state"] = target_state
        
        response = requests.post(f"{self.api_base}/execute", json=payload)
        response.raise_for_status()
        return response.json()
    
    def click(self, image_pattern: str, confidence: float = 0.9) -> Dict[str, Any]:
        """Convenience method for click actions."""
        return self.execute_action(
            "click",
            {"image_pattern": image_pattern, "confidence": confidence}
        )
    
    def type_text(self, text: str) -> Dict[str, Any]:
        """Convenience method for typing text."""
        return self.execute_action("type", {"text": text})
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Dict[str, Any]:
        """Convenience method for drag actions."""
        return self.execute_action(
            "drag",
            {
                "start_x": start_x,
                "start_y": start_y,
                "end_x": end_x,
                "end_y": end_y
            }
        )


def main():
    """Demonstrate usage of the Brobot MCP Client."""
    client = BrobotMCPClient()
    
    print("🤖 Brobot MCP Client Example\n")
    
    try:
        # 1. Get state structure
        print("1. Getting application state structure...")
        state_structure = client.get_state_structure()
        print(f"   Found {len(state_structure['states'])} states")
        for state in state_structure['states']:
            print(f"   - {state['name']}: {state['description']}")
            if state['transitions']:
                print(f"     Transitions: {[t['to_state'] for t in state['transitions']]}")
        
        # 2. Get current observation
        print("\n2. Getting current observation...")
        observation = client.get_observation()
        print(f"   Timestamp: {observation['timestamp']}")
        print(f"   Screen: {observation['screen_width']}x{observation['screen_height']}")
        print(f"   Active states:")
        for state in observation['active_states']:
            print(f"   - {state['name']} (confidence: {state['confidence']})")
        
        # 3. Execute some actions
        print("\n3. Executing actions...")
        
        # Click login button
        print("   a) Clicking login button...")
        result = client.click("login_button.png")
        print(f"      Success: {result['success']}")
        print(f"      Duration: {result['duration']:.3f}s")
        
        # Type username
        print("   b) Typing username...")
        result = client.type_text("demo_user")
        print(f"      Success: {result['success']}")
        
        # Drag element
        print("   c) Dragging element...")
        result = client.drag(100, 100, 500, 500)
        print(f"      Success: {result['success']}")
        
        # 4. Check state after actions
        print("\n4. Checking state after actions...")
        observation = client.get_observation()
        active_state = observation['active_states'][0]['name'] if observation['active_states'] else "unknown"
        print(f"   Current active state: {active_state}")
        
        # 5. Save screenshot if available
        if observation.get('screenshot'):
            print("\n5. Saving screenshot...")
            screenshot_data = base64.b64decode(observation['screenshot'])
            with open("screenshot.png", "wb") as f:
                f.write(screenshot_data)
            print("   Screenshot saved as screenshot.png")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Brobot MCP Server is running.")
        print("   Start it with: python -m mcp_server.main")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()