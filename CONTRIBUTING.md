# Contributing to Brobot MCP Server

Thank you for your interest in contributing to the Brobot MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Issues

1. **Check existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Error messages and logs

### Suggesting Features

1. **Open a discussion** first for major features
2. **Describe the use case** clearly
3. **Consider the implementation** complexity
4. **Be open to feedback** and alternatives

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation
4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: Add new automation action"
   ```
5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8+
- Java 11+
- Git

### Local Development

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/brobot-mcp-server.git
   cd brobot-mcp-server
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .[dev]
   ```

4. **Build Java CLI**:
   ```bash
   cd brobot-cli
   ./gradlew build
   ```

### Running Tests

```bash
# Python tests
pytest tests/

# Python tests with coverage
pytest --cov=mcp_server tests/

# Java tests
cd brobot-cli
./gradlew test

# Integration tests
python test_cli_integration.py
```

### Code Style

#### Python
- Follow PEP 8
- Use Black for formatting:
  ```bash
  black mcp_server tests
  ```
- Use flake8 for linting:
  ```bash
  flake8 mcp_server tests
  ```
- Use mypy for type checking:
  ```bash
  mypy mcp_server
  ```

#### Java
- Follow Google Java Style Guide
- Use Gradle's built-in formatting

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Project Structure

```
brobot-mcp-server/
├── mcp_server/          # Python server code
│   ├── api.py          # API endpoints
│   ├── models.py       # Data models
│   └── brobot_bridge.py # CLI integration
├── brobot-cli/         # Java CLI wrapper
├── brobot_client/      # Python client library
├── tests/              # Test suites
└── docs/               # Documentation
```

## Making Changes

### Adding New API Endpoints

1. Define models in `mcp_server/models.py`
2. Add endpoint in `mcp_server/api.py`
3. Update CLI if needed
4. Add tests
5. Update API documentation

Example:
```python
# models.py
class NewFeatureRequest(BaseModel):
    param1: str
    param2: int

# api.py
@router.post("/new-feature")
async def new_feature(request: NewFeatureRequest):
    # Implementation
    pass
```

### Adding New Actions

1. Define action in `brobot-cli/ExecuteActionCommand.java`
2. Add parameters model
3. Implement execution logic
4. Update client library
5. Add examples

### Improving Documentation

- Keep documentation in sync with code
- Add examples for new features
- Update troubleshooting for known issues
- Improve clarity based on user feedback

## Testing Guidelines

### Unit Tests

- Test individual functions/methods
- Mock external dependencies
- Aim for >80% coverage

```python
def test_new_feature():
    # Arrange
    client = BrobotClient()
    
    # Act
    result = client.new_feature()
    
    # Assert
    assert result.success
```

### Integration Tests

- Test full workflows
- Use real CLI (not mocks)
- Test error scenarios

### Manual Testing

Before submitting PR:
1. Test with mock data
2. Test with real Brobot CLI
3. Test client library changes
4. Verify documentation examples work

## Commit Message Guidelines

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

Examples:
```
feat: Add screenshot comparison action
fix: Handle timeout in observation endpoint
docs: Update troubleshooting guide
```

## Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **Run all tests** locally

3. **Update documentation** if needed

4. **Create PR with**:
   - Clear title and description
   - Link to related issues
   - Screenshots if UI changes

5. **Address review feedback**

6. **Squash commits** if requested

## Release Process

1. Version bumps follow semantic versioning
2. Update CHANGELOG.md
3. Tag releases
4. Publish to PyPI

## Getting Help

- **Discord**: Join our community
- **GitHub Discussions**: Ask questions
- **Issues**: Report bugs
- **Email**: maintainers@brobot.dev

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Brobot MCP Server!