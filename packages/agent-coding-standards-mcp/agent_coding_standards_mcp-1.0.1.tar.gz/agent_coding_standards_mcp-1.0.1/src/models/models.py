"""Data models for MCP server responses."""

from pydantic import BaseModel


class BackupInfo(BaseModel):
    """Backup information."""

    file_count: int  # Số files đã backup
    backup_dir: str  # Backup directory path (required, không None)


class SetupStandardsResponse(BaseModel):
    """Response model for setup_standards tool."""

    downloaded_to: str
    downloaded_files: dict[str, int]  # {subdir: số_files_downloaded}
    backup_info: BackupInfo | None = None


class SetupStandardsError(BaseModel):
    """Error response model for setup_standards tool."""

    error: str


# Union types for tools that can return success or error
SetupStandardsResult = SetupStandardsResponse | SetupStandardsError
