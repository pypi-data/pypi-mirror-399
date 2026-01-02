"""OS detection and path utilities for agents."""

import sys
from enum import Enum

from src.agent_config import AGENT_CONFIGS


class OS(Enum):
    MACOS = "macos"
    UNKNOWN = "unknown"


def detect_os() -> OS:
    """Detect if running on macOS."""
    return OS.MACOS if sys.platform == "darwin" else OS.UNKNOWN


def get_global_download_path(agent: str) -> str | None:
    """Get the global download path based on agent.

    Returns None if configuration not found or is UNSUPPORTED.
    """
    tool = agent.lower()
    config = AGENT_CONFIGS.get(tool)
    if config is None:
        return None

    # Support Pydantic model (has direct attribute access)
    global_path = config.global_path

    # Check if global_path is the string "UNSUPPORTED" or not a string
    if not isinstance(global_path, str) or global_path == "UNSUPPORTED":
        return None

    return global_path


def get_workspace_download_dir(agent: str) -> str | None:
    """Get the workspace download path based on agent.

    Returns None if configuration not found.
    workspace_dirs is expected to be a string (cross-platform path).
    """
    tool = agent.lower()
    config = AGENT_CONFIGS.get(tool)
    if config is None:
        return None

    # Support Pydantic model (has direct attribute access)
    workspace_dirs = config.workspace_dirs
    return workspace_dirs if isinstance(workspace_dirs, str) else None


def get_subdirs(agent: str) -> dict[str, str] | None:
    """Get the subdirectories configuration for an agent."""
    tool = agent.lower()
    config = AGENT_CONFIGS.get(tool)
    if config is None:
        return None

    # Support Pydantic model (has direct attribute access)
    subdirs = config.subdirs

    # Ensure we only return a dict[str, str]
    result: dict[str, str] = {}
    for k, v in subdirs.items():
        if isinstance(k, str) and isinstance(v, str):
            result[k] = v
    return result or None
