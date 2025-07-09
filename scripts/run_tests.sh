#!/bin/bash
# Script to run tests with coverage reporting

set -e

echo "=== Running Brobot MCP Server Tests ==="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Change to project root
cd "$(dirname "$0")/.."

# Create coverage directory if it doesn't exist
mkdir -p coverage

echo ""
echo "=== Installing test dependencies ==="
pip install -e ".[test]" > /dev/null 2>&1
print_status $? "Test dependencies installed"

echo ""
echo "=== Running unit tests ==="
pytest tests/unit -v -m unit
UNIT_STATUS=$?
print_status $UNIT_STATUS "Unit tests"

echo ""
echo "=== Running integration tests ==="
pytest tests/integration -v -m integration || true
INTEGRATION_STATUS=$?
print_status $INTEGRATION_STATUS "Integration tests (may fail without Java CLI)"

echo ""
echo "=== Running all tests with coverage ==="
pytest --cov=mcp_server \
       --cov-report=html:coverage/html \
       --cov-report=term-missing \
       --cov-report=xml:coverage/coverage.xml \
       -v
COVERAGE_STATUS=$?
print_status $COVERAGE_STATUS "Coverage report generated"

echo ""
echo "=== Testing client library ==="
cd brobot_client
pip install -e ".[dev]" > /dev/null 2>&1
pytest --cov=brobot_client \
       --cov-report=html:../coverage/client_html \
       --cov-report=term-missing \
       -v
CLIENT_STATUS=$?
print_status $CLIENT_STATUS "Client library tests"

cd ..

echo ""
echo "=== Test Summary ==="
echo "Coverage reports:"
echo "  - Server: coverage/html/index.html"
echo "  - Client: coverage/client_html/index.html"
echo ""

# Exit with non-zero if any tests failed
if [ $UNIT_STATUS -ne 0 ] || [ $COVERAGE_STATUS -ne 0 ] || [ $CLIENT_STATUS -ne 0 ]; then
    exit 1
fi

exit 0