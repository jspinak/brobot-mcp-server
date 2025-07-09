#!/usr/bin/env python3
"""Test script to verify CLI integration works correctly."""

import subprocess
import sys
import os
import time
import requests
import json


def build_cli():
    """Build the Brobot CLI JAR."""
    print("Building Brobot CLI...")
    
    # Change to CLI directory
    original_dir = os.getcwd()
    os.chdir("brobot-cli")
    
    try:
        # Run gradle build
        result = subprocess.run(
            ["gradle", "shadowJar"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False
        
        print("✅ CLI JAR built successfully")
        return True
    
    except FileNotFoundError:
        print("❌ Gradle not found. Please install Gradle or use ./gradlew")
        return False
    
    finally:
        os.chdir(original_dir)


def test_cli_directly():
    """Test the CLI directly to ensure it works."""
    print("\nTesting CLI directly...")
    
    jar_path = "brobot-cli/build/libs/brobot-cli.jar"
    
    if not os.path.exists(jar_path):
        print(f"❌ CLI JAR not found at {jar_path}")
        return False
    
    # Test --version
    result = subprocess.run(
        ["java", "-jar", jar_path, "--version"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ CLI version: {result.stdout.strip()}")
    else:
        print(f"❌ CLI test failed: {result.stderr}")
        return False
    
    # Test get-state-structure
    result = subprocess.run(
        ["java", "-jar", jar_path, "get-state-structure"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f"✅ State structure has {len(data.get('states', []))} states")
        except:
            print("❌ Invalid JSON from CLI")
            return False
    else:
        print(f"❌ State structure test failed: {result.stderr}")
        return False
    
    return True


def test_server_with_cli():
    """Test the server with CLI integration."""
    print("\nStarting server with CLI integration...")
    
    # Create .env file for CLI mode
    with open(".env", "w") as f:
        f.write("""# Test configuration
USE_MOCK_DATA=false
BROBOT_CLI_JAR=brobot-cli/build/libs/brobot-cli.jar
""")
    
    # Start server
    server_process = subprocess.Popen(
        [sys.executable, "-m", "mcp_server.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test health endpoint
        print("\nTesting health endpoint...")
        response = requests.get("http://localhost:8000/api/v1/health")
        data = response.json()
        print(f"Server status: {data['status']}")
        print(f"Brobot connected: {data['brobot_connected']}")
        
        if not data['brobot_connected']:
            print("❌ Brobot CLI not connected")
            return False
        
        # Test state structure
        print("\nTesting state structure endpoint...")
        response = requests.get("http://localhost:8000/api/v1/state_structure")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data['states'])} states from CLI")
        else:
            print(f"❌ State structure failed: {response.status_code}")
            return False
        
        # Test observation
        print("\nTesting observation endpoint...")
        response = requests.get("http://localhost:8000/api/v1/observation")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got observation with {len(data['active_states'])} active states")
        else:
            print(f"❌ Observation failed: {response.status_code}")
            return False
        
        # Test action execution
        print("\nTesting action execution...")
        action_request = {
            "action_type": "click",
            "parameters": {"image_pattern": "test.png"},
            "timeout": 5.0
        }
        response = requests.post(
            "http://localhost:8000/api/v1/execute",
            json=action_request
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Action executed: success={data['success']}")
        else:
            print(f"❌ Action execution failed: {response.status_code}")
            return False
        
        print("\n✅ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    finally:
        # Stop server
        server_process.terminate()
        server_process.wait()
        
        # Remove test .env
        if os.path.exists(".env"):
            os.remove(".env")


def main():
    """Run all integration tests."""
    print("=== Brobot MCP Server CLI Integration Test ===\n")
    
    # Step 1: Build CLI
    if not build_cli():
        print("\n❌ CLI build failed. Cannot continue.")
        return 1
    
    # Step 2: Test CLI directly
    if not test_cli_directly():
        print("\n❌ CLI tests failed. Cannot continue.")
        return 1
    
    # Step 3: Test server with CLI
    if not test_server_with_cli():
        print("\n❌ Server integration tests failed.")
        return 1
    
    print("\n✅ All tests passed! The CLI integration is working correctly.")
    print("\nTo use the CLI integration:")
    print("1. Set USE_MOCK_DATA=false in your .env file")
    print("2. Set BROBOT_CLI_JAR=brobot-cli/build/libs/brobot-cli.jar")
    print("3. Start the server: python -m mcp_server.main")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())