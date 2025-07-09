# Multi-stage build for Brobot MCP Server

# Stage 1: Build Java CLI
FROM gradle:8-jdk17 AS java-builder

WORKDIR /build

# Copy Gradle files
COPY brobot-cli/build.gradle brobot-cli/settings.gradle brobot-cli/gradle.properties ./brobot-cli/
COPY brobot-cli/gradle ./brobot-cli/gradle

# Download dependencies
WORKDIR /build/brobot-cli
RUN gradle dependencies --no-daemon

# Copy source code
COPY brobot-cli/src ./src

# Build JAR
RUN gradle shadowJar --no-daemon

# Stage 2: Python runtime
FROM python:3.11-slim

# Install Java runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash brobot

# Set working directory
WORKDIR /app

# Copy Python requirements first for better caching
COPY pyproject.toml README.md ./
COPY mcp_server ./mcp_server

# Install Python dependencies
RUN pip install --no-cache-dir -e . && \
    pip cache purge

# Copy Java CLI from builder
COPY --from=java-builder /build/brobot-cli/build/libs/brobot-cli*.jar /app/brobot-cli.jar

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R brobot:brobot /app

# Switch to non-root user
USER brobot

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    BROBOT_CLI_JAR=/app/brobot-cli.jar \
    USE_MOCK_DATA=false \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${MCP_PORT}/health || exit 1

# Expose port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"]