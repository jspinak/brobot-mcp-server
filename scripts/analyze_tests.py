#!/usr/bin/env python3
"""Analyze test coverage and structure without running tests."""

import ast
import re
from pathlib import Path
from collections import defaultdict

def analyze_test_file(file_path):
    """Analyze a test file and extract test information."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    test_classes = []
    test_functions = []
    fixtures = []
    markers = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name.startswith("Test"):
                test_methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                        test_methods.append(item.name)
                test_classes.append({
                    'name': node.name,
                    'methods': test_methods,
                    'docstring': ast.get_docstring(node)
                })
        
        elif isinstance(node, ast.FunctionDef):
            if node.name.startswith("test_"):
                test_functions.append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node)
                })
            
            # Check for fixtures
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "fixture":
                    fixtures.append(node.name)
                elif isinstance(decorator, ast.Attribute):
                    if decorator.attr == "fixture":
                        fixtures.append(node.name)
    
    # Extract markers from content
    marker_pattern = r'@pytest\.mark\.(\w+)'
    markers.update(re.findall(marker_pattern, content))
    
    return {
        'classes': test_classes,
        'functions': test_functions,
        'fixtures': fixtures,
        'markers': list(markers),
        'total_tests': sum(len(c['methods']) for c in test_classes) + len(test_functions)
    }

def generate_test_report():
    """Generate a comprehensive test report."""
    project_root = Path(__file__).parent.parent
    
    print("Brobot MCP Server - Test Analysis Report")
    print("=" * 80)
    
    # Analyze all test files
    test_data = defaultdict(dict)
    
    # Unit tests
    unit_test_dir = project_root / "tests" / "unit"
    for test_file in unit_test_dir.glob("test_*.py"):
        module_name = test_file.stem.replace("test_", "")
        test_data['unit'][module_name] = analyze_test_file(test_file)
    
    # Integration tests
    integration_test_dir = project_root / "tests" / "integration"
    for test_file in integration_test_dir.glob("test_*.py"):
        module_name = test_file.stem.replace("test_", "")
        test_data['integration'][module_name] = analyze_test_file(test_file)
    
    # Client tests
    client_test_dir = project_root / "brobot_client" / "tests"
    for test_file in client_test_dir.glob("test_*.py"):
        module_name = test_file.stem.replace("test_", "")
        test_data['client'][module_name] = analyze_test_file(test_file)
    
    # Print unit test summary
    print("\nUNIT TESTS")
    print("-" * 80)
    total_unit_tests = 0
    for module, data in test_data['unit'].items():
        print(f"\n{module}.py:")
        print(f"  Total tests: {data['total_tests']}")
        if data['classes']:
            print("  Test classes:")
            for cls in data['classes']:
                print(f"    - {cls['name']} ({len(cls['methods'])} tests)")
                if len(cls['methods']) <= 5:
                    for method in cls['methods']:
                        print(f"      • {method}")
        if data['markers']:
            print(f"  Markers: {', '.join(data['markers'])}")
        total_unit_tests += data['total_tests']
    
    print(f"\nTotal unit tests: {total_unit_tests}")
    
    # Print integration test summary
    print("\n\nINTEGRATION TESTS")
    print("-" * 80)
    total_integration_tests = 0
    for module, data in test_data['integration'].items():
        print(f"\n{module}.py:")
        print(f"  Total tests: {data['total_tests']}")
        if data['classes']:
            print("  Test classes:")
            for cls in data['classes']:
                print(f"    - {cls['name']} ({len(cls['methods'])} tests)")
        if data['markers']:
            print(f"  Markers: {', '.join(data['markers'])}")
        total_integration_tests += data['total_tests']
    
    print(f"\nTotal integration tests: {total_integration_tests}")
    
    # Print client test summary
    print("\n\nCLIENT TESTS")
    print("-" * 80)
    total_client_tests = 0
    for module, data in test_data['client'].items():
        print(f"\n{module}.py:")
        print(f"  Total tests: {data['total_tests']}")
        if data['classes']:
            print("  Test classes:")
            for cls in data['classes']:
                print(f"    - {cls['name']} ({len(cls['methods'])} tests)")
        total_client_tests += data['total_tests']
    
    print(f"\nTotal client tests: {total_client_tests}")
    
    # Overall summary
    print("\n\nOVERALL TEST SUMMARY")
    print("=" * 80)
    print(f"Unit tests:        {total_unit_tests}")
    print(f"Integration tests: {total_integration_tests}")
    print(f"Client tests:      {total_client_tests}")
    print(f"TOTAL TESTS:       {total_unit_tests + total_integration_tests + total_client_tests}")
    
    # Markers summary
    all_markers = set()
    for category in test_data.values():
        for module_data in category.values():
            all_markers.update(module_data['markers'])
    
    if all_markers:
        print(f"\nTest markers used: {', '.join(sorted(all_markers))}")
    
    # Coverage estimation
    print("\n\nCOVERAGE ESTIMATION")
    print("-" * 80)
    source_modules = [
        "config", "models", "api", "brobot_bridge", "main"
    ]
    
    for module in source_modules:
        if module in test_data['unit']:
            test_count = test_data['unit'][module]['total_tests']
            status = "✓" if test_count > 5 else "⚠" if test_count > 0 else "✗"
            print(f"{status} {module}.py: {test_count} tests")
        else:
            print(f"✗ {module}.py: No tests found")

if __name__ == "__main__":
    generate_test_report()