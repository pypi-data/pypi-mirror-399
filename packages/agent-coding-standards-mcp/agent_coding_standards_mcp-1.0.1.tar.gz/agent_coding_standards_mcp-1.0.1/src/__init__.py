"""MCP Server for AI coding agent standards."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agent-coding-standards-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
