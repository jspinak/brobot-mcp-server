#!/usr/bin/env python3
"""Basic test runner to verify code structure and imports without pytest."""

import sys
import os
import importlib
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    modules_to_test = [
        "mcp_server",
        "mcp_server.config",
        "mcp_server.models",
        "mcp_server.api",
        "mcp_server.brobot_bridge",
        "mcp_server.main",
    ]
    
    print("Testing module imports...")
    failed = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append((module, e))
    
    return len(failed) == 0, failed

def test_file_structure():
    """Test that all expected files exist."""
    expected_files = [
        "pyproject.toml",
        "README.md",
        "mcp_server/__init__.py",
        "mcp_server/config.py",
        "mcp_server/models.py",
        "mcp_server/api.py",
        "mcp_server/brobot_bridge.py",
        "mcp_server/main.py",
        "tests/conftest.py",
        "tests/unit/test_api.py",
        "tests/unit/test_models.py",
        "tests/unit/test_config.py",
        "tests/unit/test_brobot_bridge.py",
        "brobot_client/pyproject.toml",
        "brobot_client/brobot_client/__init__.py",
        "brobot_client/brobot_client/client.py",
        "brobot_client/brobot_client/async_client.py",
    ]
    
    print("\nChecking file structure...")
    missing = []
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            missing.append(file_path)
    
    return len(missing) == 0, missing

def test_basic_functionality():
    """Test basic functionality without running actual tests."""
    print("\nTesting basic functionality...")
    tests_passed = []
    tests_failed = []
    
    # Test 1: Config can be instantiated
    try:
        from mcp_server.config import Settings
        settings = Settings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        print("✓ Config: Settings can be instantiated with defaults")
        tests_passed.append("Config defaults")
    except Exception as e:
        print(f"✗ Config: {e}")
        tests_failed.append(("Config", e))
    
    # Test 2: Models can be created
    try:
        from mcp_server.models import State, StateStructure
        state = State(name="test_state")
        assert state.name == "test_state"
        print("✓ Models: State model can be created")
        tests_passed.append("Models")
    except Exception as e:
        print(f"✗ Models: {e}")
        tests_failed.append(("Models", e))
    
    # Test 3: FastAPI app exists
    try:
        from mcp_server.main import app
        assert app.title == "Brobot MCP Server"
        print("✓ FastAPI: App is properly configured")
        tests_passed.append("FastAPI app")
    except Exception as e:
        print(f"✗ FastAPI: {e}")
        tests_failed.append(("FastAPI", e))
    
    # Test 4: Client can be imported
    try:
        sys.path.insert(0, str(project_root / "brobot_client"))
        from brobot_client import BrobotClient
        print("✓ Client: BrobotClient can be imported")
        tests_passed.append("Client import")
    except Exception as e:
        print(f"✗ Client: {e}")
        tests_failed.append(("Client", e))
    
    return len(tests_failed) == 0, (tests_passed, tests_failed)

def main():
    """Run all basic tests."""
    print("=" * 60)
    print("Basic Test Runner for Brobot MCP Server")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    imports_ok, failed_imports = test_imports()
    all_passed &= imports_ok
    
    # Test file structure
    files_ok, missing_files = test_file_structure()
    all_passed &= files_ok
    
    # Test basic functionality
    func_ok, (passed_tests, failed_tests) = test_basic_functionality()
    all_passed &= func_ok
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("✓ All basic tests passed!")
        return 0
    else:
        print("✗ Some tests failed:")
        if failed_imports:
            print(f"  - {len(failed_imports)} import failures")
        if missing_files:
            print(f"  - {len(missing_files)} missing files")
        if failed_tests:
            print(f"  - {len(failed_tests)} functionality test failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())