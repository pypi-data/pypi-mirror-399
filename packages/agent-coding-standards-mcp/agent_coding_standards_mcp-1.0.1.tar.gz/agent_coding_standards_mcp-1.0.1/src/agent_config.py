"""Agent configuration management."""

from pydantic import BaseModel, ConfigDict


class AgentConfig(BaseModel):
    """Configuration for a single agent."""

    model_config = ConfigDict(extra="allow")  # Allow new fields for future extensions

    global_path: str
    workspace_dirs: str
    subdirs: dict[str, str]


# Define agent configs
AGENT_CONFIGS: dict[str, AgentConfig] = {
    "cline": AgentConfig(
        global_path="~/Documents/Cline",
        workspace_dirs="/.clinerules",
        subdirs={
            "rules": "Rules",
            "workflows": "Workflows",
        },
    ),
    "claude": AgentConfig(
        global_path="~/.claude",
        workspace_dirs="/.claude",
        subdirs={
            "agents": "agents",
            "commands": "commands",
            "skills": "skills",
        },
    ),
    "copilot": AgentConfig(
        global_path="~/Library/Application Support/Code/User/prompts",
        workspace_dirs="/.github",
        subdirs={
            "prompts": ".",
            "agents": ".",
            "instructions": ".",
        },
    ),
}
