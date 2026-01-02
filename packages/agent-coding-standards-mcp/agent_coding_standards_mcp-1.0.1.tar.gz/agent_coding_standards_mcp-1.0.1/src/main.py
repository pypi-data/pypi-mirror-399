"""Main entry point for MCP Server."""

# Initialize logging configuration - this ensures logging is set up for the entire application
from mcp.server import FastMCP

import src.logging_config  # noqa: F401
from src.tools import setup_standards

# Create an MCP server
mcp = FastMCP(
    name="agent-coding-standards-mcp",
    instructions="A MCP server for setting up coding standards for AI coding agents",
    json_response=True,
)

# Add the setup standards tool
mcp.add_tool(setup_standards)


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
