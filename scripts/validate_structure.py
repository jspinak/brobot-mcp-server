#!/usr/bin/env python3
"""Validate project structure and Python syntax without dependencies."""

import ast
import sys
from pathlib import Path

def validate_python_syntax(file_path):
    """Validate that a Python file has correct syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def validate_project_structure():
    """Validate the complete project structure."""
    project_root = Path(__file__).parent.parent
    
    print("Brobot MCP Server - Structure Validation")
    print("=" * 60)
    
    # Define expected structure
    structure = {
        "Server Package": [
            "mcp_server/__init__.py",
            "mcp_server/config.py",
            "mcp_server/models.py",
            "mcp_server/api.py",
            "mcp_server/brobot_bridge.py",
            "mcp_server/main.py",
        ],
        "Client Package": [
            "brobot_client/brobot_client/__init__.py",
            "brobot_client/brobot_client/client.py",
            "brobot_client/brobot_client/async_client.py",
            "brobot_client/brobot_client/exceptions.py",
        ],
        "Tests": [
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/utils.py",
            "tests/factories.py",
            "tests/unit/__init__.py",
            "tests/unit/test_api.py",
            "tests/unit/test_models.py",
            "tests/unit/test_config.py",
            "tests/unit/test_brobot_bridge.py",
            "tests/unit/test_main.py",
            "tests/integration/__init__.py",
            "tests/integration/test_server_cli_integration.py",
            "tests/integration/test_client_server_integration.py",
            "brobot_client/tests/__init__.py",
            "brobot_client/tests/test_sync_client.py",
            "brobot_client/tests/test_async_client.py",
            "brobot_client/tests/test_exceptions.py",
        ],
        "Configuration": [
            "pyproject.toml",
            "brobot_client/pyproject.toml",
            ".gitignore",
            "README.md",
            "brobot_client/README.md",
            "tox.ini",
            ".pre-commit-config.yaml",
            ".yamllint.yml",
            ".markdownlint.json",
            ".bandit",
            "sonar-project.properties",
        ],
        "CI/CD": [
            ".github/workflows/test.yml",
            ".github/workflows/publish.yml",
            ".github/workflows/build-cli.yml",
            ".github/workflows/code-quality.yml",
            ".github/workflows/dependency-scan.yml",
            ".github/workflows/release.yml",
            ".github/dependabot.yml",
            ".github/CI_CD_GUIDE.md",
        ],
        "Docker": [
            "Dockerfile",
            "Dockerfile.dev",
            "docker-compose.yml",
            ".dockerignore",
        ],
        "Scripts": [
            "scripts/run_tests.sh",
            "scripts/basic_test.py",
        ],
        "Java CLI": [
            "brobot-cli/build.gradle",
            "brobot-cli/settings.gradle",
            "brobot-cli/gradle.properties",
            "brobot-cli/src/main/java/io/github/jspinak/brobot/cli/BrobotCLI.java",
            "brobot-cli/src/main/java/io/github/jspinak/brobot/cli/commands/GetStateStructureCommand.java",
            "brobot-cli/src/main/java/io/github/jspinak/brobot/cli/commands/GetObservationCommand.java",
            "brobot-cli/src/main/java/io/github/jspinak/brobot/cli/commands/ExecuteActionCommand.java",
        ],
    }
    
    all_valid = True
    total_files = 0
    valid_files = 0
    
    for category, files in structure.items():
        print(f"\n{category}:")
        print("-" * 40)
        
        for file_path in files:
            total_files += 1
            full_path = project_root / file_path
            
            if not full_path.exists():
                print(f"✗ {file_path} - NOT FOUND")
                all_valid = False
                continue
            
            # For Python files, check syntax
            if file_path.endswith('.py'):
                syntax_ok, error = validate_python_syntax(full_path)
                if syntax_ok:
                    print(f"✓ {file_path}")
                    valid_files += 1
                else:
                    print(f"✗ {file_path} - {error}")
                    all_valid = False
            else:
                print(f"✓ {file_path}")
                valid_files += 1
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total files checked: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Missing/Invalid files: {total_files - valid_files}")
    
    if all_valid:
        print("\n✓ All files present and valid!")
        return 0
    else:
        print("\n✗ Some files are missing or invalid")
        return 1

def check_test_count():
    """Count the number of test files and test functions."""
    project_root = Path(__file__).parent.parent
    
    print("\n" + "=" * 60)
    print("TEST COVERAGE SUMMARY")
    print("=" * 60)
    
    test_dirs = [
        project_root / "tests" / "unit",
        project_root / "tests" / "integration",
        project_root / "brobot_client" / "tests",
    ]
    
    total_test_files = 0
    total_test_functions = 0
    
    for test_dir in test_dirs:
        if not test_dir.exists():
            continue
            
        test_files = list(test_dir.glob("test_*.py"))
        total_test_files += len(test_files)
        
        dir_test_count = 0
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    # Count test functions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                            dir_test_count += 1
            except:
                pass
        
        total_test_functions += dir_test_count
        rel_path = test_dir.relative_to(project_root)
        print(f"{rel_path}: {len(test_files)} files, {dir_test_count} test functions")
    
    print(f"\nTotal: {total_test_files} test files, {total_test_functions} test functions")

if __name__ == "__main__":
    exit_code = validate_project_structure()
    check_test_count()
    sys.exit(exit_code)