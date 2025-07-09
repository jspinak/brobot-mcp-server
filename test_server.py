#!/usr/bin/env python3
"""Quick test script to verify the server runs correctly."""

import requests
import time
import subprocess
import sys

def test_server():
    """Test that the server starts and responds to health check."""
    print("Starting Brobot MCP Server...")
    
    # Start the server in a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "-m", "mcp_server.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server time to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        print(f"Health check status code: {response.status_code}")
        print(f"Health check response: {response.json()}")
        
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        print(f"\nRoot endpoint response: {response.json()}")
        
        print("\n✅ Server is running successfully!")
        print("Visit http://localhost:8000/docs for interactive API documentation")
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_server()