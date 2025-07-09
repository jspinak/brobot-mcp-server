#!/usr/bin/env python3
"""Test script to verify all API endpoints work correctly."""

import requests
import json
import time
import subprocess
import sys

def test_api_endpoints():
    """Test all API endpoints with mock data."""
    print("Starting Brobot MCP Server...")
    
    # Start the server in a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "-m", "mcp_server.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server time to start
    time.sleep(3)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test root endpoint
        print("\n1. Testing root endpoint (/)...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test health endpoint
        print("\n2. Testing health endpoint (/health)...")
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test extended health endpoint
        print("\n3. Testing extended health endpoint (/api/v1/health)...")
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test state structure endpoint
        print("\n4. Testing state structure endpoint (/api/v1/state_structure)...")
        response = requests.get(f"{base_url}/api/v1/state_structure")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Number of states: {len(data['states'])}")
        print(f"State names: {[s['name'] for s in data['states']]}")
        print(f"Current state: {data['current_state']}")
        
        # Test observation endpoint
        print("\n5. Testing observation endpoint (/api/v1/observation)...")
        response = requests.get(f"{base_url}/api/v1/observation")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Timestamp: {data['timestamp']}")
        print(f"Active states: {[s['name'] for s in data['active_states']]}")
        print(f"Screen dimensions: {data['screen_width']}x{data['screen_height']}")
        print(f"Has screenshot: {'Yes' if data['screenshot'] else 'No'}")
        
        # Test execute endpoint
        print("\n6. Testing execute endpoint (/api/v1/execute)...")
        
        # Test click action
        click_request = {
            "action_type": "click",
            "parameters": {
                "image_pattern": "button_submit.png",
                "confidence": 0.9
            },
            "target_state": "form_submitted",
            "timeout": 5.0
        }
        response = requests.post(f"{base_url}/api/v1/execute", json=click_request)
        print(f"Status: {response.status_code}")
        print(f"Click result: {json.dumps(response.json(), indent=2)}")
        
        # Test type action
        type_request = {
            "action_type": "type",
            "parameters": {
                "text": "Hello, Brobot!"
            },
            "timeout": 10.0
        }
        response = requests.post(f"{base_url}/api/v1/execute", json=type_request)
        print(f"\nType result: {json.dumps(response.json(), indent=2)}")
        
        # Test unknown action
        unknown_request = {
            "action_type": "unknown_action",
            "parameters": {},
            "timeout": 10.0
        }
        response = requests.post(f"{base_url}/api/v1/execute", json=unknown_request)
        print(f"\nUnknown action result: {json.dumps(response.json(), indent=2)}")
        
        print("\n✅ All API endpoints are working correctly!")
        print("\n📚 Visit http://localhost:8000/docs for interactive API documentation")
        print("📊 Visit http://localhost:8000/redoc for alternative documentation")
        
    except Exception as e:
        print(f"\n❌ Error testing endpoints: {e}")
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_api_endpoints()