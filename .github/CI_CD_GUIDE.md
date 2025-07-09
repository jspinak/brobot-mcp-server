# CI/CD Pipeline Guide

This document describes the continuous integration and deployment pipeline for Brobot MCP Server.

## Overview

The CI/CD pipeline consists of several GitHub Actions workflows that automate testing, building, and deployment processes.

## Workflows

### 1. Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual dispatch

**Jobs:**
- **Lint:** Code style and static analysis
- **Test Python:** Unit tests across multiple Python versions (3.8-3.12) and OS (Ubuntu, Windows, macOS)
- **Test Client:** Client library tests
- **Test Integration:** Integration tests with Java CLI
- **Test Docker:** Docker build verification
- **Security Scan:** Trivy vulnerability scanning

### 2. Build CLI Workflow (`build-cli.yml`)

**Triggers:**
- Changes to `brobot-cli/` directory
- Pull requests affecting CLI
- Manual dispatch

**Jobs:**
- Build Java CLI on multiple OS and Java versions (11, 17, 21)
- Run Java tests with JaCoCo coverage
- Integration test with Python server

### 3. Code Quality Workflow (`code-quality.yml`)

**Triggers:**
- Push to main branches
- Pull requests
- Weekly schedule (Sunday midnight)

**Jobs:**
- **Pre-commit hooks:** Automated formatting and linting
- **Python quality:** Black, isort, Flake8, Pylint, MyPy, Bandit
- **Java quality:** Checkstyle, SpotBugs
- **SonarCloud:** Comprehensive code analysis
- **Markdown/YAML lint:** Documentation quality

### 4. Dependency Scan Workflow (`dependency-scan.yml`)

**Triggers:**
- Push to main branches
- Pull requests
- Weekly schedule (Monday morning)

**Jobs:**
- **Python dependencies:** Safety, pip-audit
- **Java dependencies:** OWASP Dependency Check
- **Snyk scan:** Vulnerability detection
- **Trivy scan:** Container and filesystem scanning
- **License check:** Compatibility verification

### 5. Publish Workflow (`publish.yml`)

**Triggers:**
- Release publication
- Manual dispatch with version input

**Jobs:**
- Build Python packages (server and client)
- Build Java CLI JAR
- Publish to PyPI
- Publish Docker images to Docker Hub and GitHub Container Registry
- Create GitHub release assets

### 6. Release Workflow (`release.yml`)

**Triggers:**
- Manual dispatch with version and pre-release flag

**Jobs:**
- Prepare release (version updates, changelog)
- Run full test suite
- Create GitHub release
- Trigger publish workflow
- Update documentation
- Post-release tasks (milestones, announcements)

## Configuration Files

### Pre-commit Configuration (`.pre-commit-config.yaml`)
- Automated code formatting (Black, isort)
- Linting (Flake8, MyPy, Bandit)
- File checks (YAML, JSON, merge conflicts)
- Commit message validation (Commitizen)

### Code Quality Tools
- **`.yamllint.yml`**: YAML linting rules
- **`.markdownlint.json`**: Markdown style rules
- **`.bandit`**: Security linting configuration
- **`sonar-project.properties`**: SonarCloud analysis settings

### Dependency Management
- **`.github/dependabot.yml`**: Automated dependency updates
- Separate configurations for Python, Java, GitHub Actions, and Docker

### Docker Configuration
- **`Dockerfile`**: Production multi-stage build
- **`Dockerfile.dev`**: Development environment with hot reload
- **`docker-compose.yml`**: Local development stack
- **`.dockerignore`**: Build optimization

## Local Development

### Running Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Running Tests Locally
```bash
# Run all tests with coverage
./scripts/run_tests.sh

# Run specific test suite
pytest tests/unit -v
pytest tests/integration -v

# Run with tox for multiple Python versions
tox
```

### Code Quality Checks
```bash
# Format code
black mcp_server tests
isort mcp_server tests

# Lint code
flake8 mcp_server tests
mypy mcp_server

# Security scan
bandit -r mcp_server
```

### Docker Development
```bash
# Build and run production image
docker-compose up brobot-mcp-server

# Run development environment with hot reload
docker-compose --profile dev up brobot-mcp-dev

# Run with additional services
docker-compose --profile with-redis --profile with-postgres up
```

## Release Process

### 1. Prepare Release
```bash
# Trigger release workflow
# Go to Actions → Release → Run workflow
# Enter version (e.g., 0.1.0) and pre-release flag
```

### 2. Review and Merge
- Review automatically created PR
- Ensure all checks pass
- Merge PR to main

### 3. Publish Release
- Go to Releases page
- Review draft release
- Edit if needed
- Publish release (triggers publish workflow)

### 4. Verify Deployment
```bash
# Check PyPI
pip install brobot-mcp-server==<version>

# Check Docker Hub
docker pull <username>/brobot-mcp-server:<version>

# Check GitHub Container Registry
docker pull ghcr.io/<org>/brobot-mcp-server:<version>
```

## Secrets Configuration

Required GitHub repository secrets:
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub access token
- `SONAR_TOKEN`: SonarCloud authentication token
- `SNYK_TOKEN`: Snyk authentication token
- `SAFETY_API_KEY`: Safety API key (optional)

## Best Practices

1. **Commit Messages**: Follow conventional commits format
   ```
   type(scope): description
   
   Examples:
   feat(api): add new endpoint for state transitions
   fix(client): handle connection timeouts properly
   docs(readme): update installation instructions
   ```

2. **Branch Protection**: Enable for `main` branch
   - Require PR reviews
   - Require status checks (tests, linting)
   - Require up-to-date branches

3. **Pull Request Process**:
   - Create feature branch from `develop`
   - Ensure all tests pass
   - Update documentation if needed
   - Request review
   - Squash and merge

4. **Version Bumping**:
   - Patch: Bug fixes (0.1.0 → 0.1.1)
   - Minor: New features (0.1.0 → 0.2.0)
   - Major: Breaking changes (0.1.0 → 1.0.0)

## Monitoring

### Build Status
- Check Actions tab for workflow runs
- Review test coverage reports
- Monitor dependency updates

### Code Quality
- SonarCloud dashboard for code quality metrics
- Security alerts in Security tab
- Dependabot alerts for vulnerabilities

### Performance
- Docker image size optimization
- Build time metrics in Actions
- Test execution time trends

## Troubleshooting

### Common Issues

1. **Test Failures**
   - Check test logs in Actions
   - Run tests locally to reproduce
   - Verify environment variables

2. **Build Failures**
   - Check dependency versions
   - Clear caches in Actions
   - Verify Docker build context

3. **Publishing Issues**
   - Verify PyPI/Docker credentials
   - Check version conflicts
   - Review publish logs

### Cache Management
```yaml
# Clear GitHub Actions cache
# Go to Actions → Caches → Delete specific caches
```

### Manual Deployment
If automated deployment fails:
```bash
# Build and publish Python package
python -m build
twine upload dist/*

# Build and push Docker image
docker build -t brobot-mcp-server .
docker push <registry>/brobot-mcp-server:latest
```

## Future Improvements

1. **Add E2E Tests**: Selenium/Playwright for UI automation testing
2. **Performance Testing**: Load testing with Locust or K6
3. **Multi-arch Builds**: ARM64 support for M1 Macs
4. **Deployment Automation**: Kubernetes manifests, Helm charts
5. **Monitoring**: Prometheus metrics, Grafana dashboards