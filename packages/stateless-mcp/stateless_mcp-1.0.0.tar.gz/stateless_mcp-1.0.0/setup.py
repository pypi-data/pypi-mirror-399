"""Setup configuration for stateless-mcp."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stateless-mcp",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A stateless JSON-RPC 2.0 server with streaming support for MCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stateless-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "black>=23.11.0",
            "ruff>=0.1.6",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stateless-mcp=stateless_mcp.app:main",
        ],
    },
)
