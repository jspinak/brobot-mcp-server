"""Setup configuration for brobot-client package."""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
version = {}
with open(os.path.join("brobot_client", "__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="brobot-client",
    version=version.get("__version__", "0.1.0"),
    author="Brobot MCP Contributors",
    author_email="",
    description="Python client library for Brobot MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jspinak/brobot-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "types-requests",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/jspinak/brobot-mcp-server/issues",
        "Source": "https://github.com/jspinak/brobot-mcp-server",
        "Documentation": "https://github.com/jspinak/brobot-mcp-server/tree/main/brobot_client",
    },
)