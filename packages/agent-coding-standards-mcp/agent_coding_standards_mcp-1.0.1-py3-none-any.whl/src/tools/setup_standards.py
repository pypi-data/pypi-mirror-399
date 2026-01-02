"""Setup coding standards from GitLab repository."""

import asyncio
import os
import shutil
from collections import defaultdict
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from src.logging_config import logger
from src.models.models import (
    BackupInfo,
    SetupStandardsError,
    SetupStandardsResponse,
    SetupStandardsResult,
)
from src.services.gitlab_service import Gitlab
from src.utils.os_utils import (
    get_global_download_path,
    get_subdirs,
    get_workspace_download_dir,
)

BATCH_SIZE = 5
GUIDELINES_BASE = "guidelines"


AGENT_OPTIONS = Literal["cline", "claude", "copilot"]


async def setup_standards(
    agent: Annotated[
        AGENT_OPTIONS,
        Field(description="Tool name (e.g., 'cline', 'claude', 'copilot')"),
    ],
    is_scope_global: Annotated[
        bool,
        Field(description="true for global path, false for workspace path"),
    ] = True,
    workspace_path: Annotated[
        str | None,
        Field(description="Absolute directory path when using workspace scope."),
    ] = None,
    overwrite: Annotated[
        bool,
        Field(description="true to overwrite without backup, false to create backup"),
    ] = True,
) -> SetupStandardsResult:
    """Setup coding standards from GitLab.

    MUST present these 4 options immediately in a single prompt:
    1. Default (Global, no backup)
    2. Global with backup
    3. Workspace, no backup
    4. Workspace with backup

    For option 3 or 4: If user is on an IDE/editor that supports workspace folders,
    suggest the workspace root as the workspace_path.

    After user selects an option, show all settings and ask for confirmation before executing.
    """

    try:
        # 1. Validate & resolve final path
        final_path = _resolve_path(agent, is_scope_global, workspace_path)
        if isinstance(final_path, SetupStandardsError):
            return final_path

        # 2. Get subdirs config
        subdirs = get_subdirs(agent)
        if not subdirs:
            return SetupStandardsError(
                error=f"No subdirectories configured for agent '{agent}'"
            )

        # 3. Group subdirs by workspace_dir (handle multiple subdirs -> same workspace_dir)
        dir_groups = _group_subdirs_by_workspace_dir(
            subdirs, final_path, is_scope_global
        )

        # 4. Collect all files from all groups
        all_files_by_workspace_dir = await _collect_all_files_from_groups(
            agent, dir_groups, final_path, is_scope_global
        )
        if isinstance(all_files_by_workspace_dir, SetupStandardsError):
            return all_files_by_workspace_dir

        # 5. Backup once for all files
        backup_created, backup_path, total_files_backed_up = (
            _backup_all_conflicting_files(
                final_path, all_files_by_workspace_dir, overwrite
            )
        )

        # 6. Process each workspace_dir to download (backup already done)
        results = {}
        for workspace_dir, group in dir_groups.items():
            group_results = await _process_workspace_dir(
                agent,
                workspace_dir,
                group,
                overwrite,
                final_path,
            )
            if isinstance(group_results, SetupStandardsError):
                return group_results
            results[workspace_dir] = group_results

        # 7. Create backup_info
        backup_info = None
        if backup_created and backup_path:
            backup_info = BackupInfo(
                file_count=total_files_backed_up, backup_dir=backup_path
            )

        # 8. Collect downloaded_files from results (flatten dict[workspace_dir, dict[str, int]])
        downloaded_files = {}
        for group_results in results.values():
            downloaded_files.update(group_results)

        return SetupStandardsResponse(
            downloaded_to=final_path,
            downloaded_files=downloaded_files,
            backup_info=backup_info,
        )

    except Exception as e:
        logger.exception("Setup failed")
        return SetupStandardsError(error=str(e))


def _resolve_path(
    tool: str, is_global: bool, workspace_path: str | None
) -> str | SetupStandardsError:
    """Resolve and validate final download path."""
    if is_global:
        path = get_global_download_path(tool)
        if not path:
            return SetupStandardsError(
                error=f"No global path: Global setup is not supported for '{tool}'"
            )
        return os.path.expanduser(path)

    # Workspace scope
    if not workspace_path:
        return SetupStandardsError(
            error="workspace_path required: Parameter 'workspace_path' is required when 'is_scope_global=false'"
        )

    # Allow ~/... by expanding user first, then require absolute path
    workspace_path = os.path.expanduser(workspace_path)
    if not os.path.isabs(workspace_path):
        return SetupStandardsError(
            error=f"Parameter 'workspace_path' must be absolute path, got: {workspace_path}"
        )

    suffix = get_workspace_download_dir(tool)
    if not suffix:
        return SetupStandardsError(
            error=f"Workspace setup is not supported for agent '{tool}'"
        )

    return os.path.join(workspace_path.rstrip("/"), suffix.lstrip("/"))


def _group_subdirs_by_workspace_dir(
    subdirs: dict[str, str], final_path: str, is_global: bool
) -> dict[str, list[tuple[str, str]]]:
    """Group subdirs by their workspace_dir path.

    Returns: {workspace_dir: [(subdir, display_name), ...]}
    """
    groups = defaultdict(list)
    for subdir, display_name in subdirs.items():
        workspace_dir = _calc_workspace_dir(final_path, subdir, display_name, is_global)
        groups[workspace_dir].append((subdir, display_name))
    return dict(groups)


def _calc_workspace_dir(
    final_path: str, subdir: str, display_name: str, is_global: bool
) -> str:
    """Calculate workspace directory path for a subdir."""
    if is_global and display_name == ".":
        return final_path
    suffix = display_name if is_global else subdir
    return f"{final_path}/{suffix}"


def _relative_path(gitlab_path: str, gitlab_file_path: str) -> str:
    """Return relative path of gitlab_file_path under gitlab_path."""
    if gitlab_file_path.startswith(gitlab_path + "/"):
        return gitlab_file_path[len(gitlab_path) + 1 :]
    if gitlab_file_path == gitlab_path:
        return os.path.basename(gitlab_file_path)
    return os.path.basename(gitlab_file_path)


async def _collect_all_files_from_groups(
    tool: str,
    dir_groups: dict[str, list[tuple[str, str]]],
    final_path: str,
    is_scope_global: bool,
) -> dict[str, list[str]] | SetupStandardsError:
    """Collect all files from all groups before processing.

    Fetches trees from GitLab for all groups and collects workspace file paths.

    Args:
        tool: Agent name
        dir_groups: Dictionary mapping workspace_dir to list of (subdir, display_name) tuples
        final_path: Final download path
        is_scope_global: Whether using global scope

    Returns:
        Dictionary mapping workspace_dir to list of workspace file paths,
        or SetupStandardsError if any group fails to fetch
    """
    all_files_by_workspace_dir = {}

    for workspace_dir, group in dir_groups.items():
        files = []

        # Fetch trees for all subdirs in this group
        for subdir, _display_name in group:
            gitlab_path = f"{GUIDELINES_BASE}/{tool}/{subdir}"
            tree = await Gitlab.get_repository_tree(gitlab_path)

            if not tree:
                # ❌ ANY failure → return error immediately (no partial success)
                return SetupStandardsError(
                    error=f"GitLab error: No files in repository path '{gitlab_path}'"
                )

            # Collect workspace file paths from this tree
            for item in tree:
                if item["type"] == "blob":
                    gitlab_file_path = item["path"]
                    relative_path = _relative_path(gitlab_path, gitlab_file_path)
                    workspace_path = os.path.join(workspace_dir, relative_path)
                    files.append(workspace_path)

        all_files_by_workspace_dir[workspace_dir] = files

    return all_files_by_workspace_dir


def _backup_all_conflicting_files(
    final_path: str,
    all_files_by_workspace_dir: dict[str, list[str]],
    overwrite: bool,
) -> tuple[bool, str | None, int]:
    """Backup all conflicting files once at final_path level.

    Args:
        final_path: Parent directory path where backup will be created
        all_files_by_workspace_dir: Dictionary mapping workspace_dir to list of file paths
        overwrite: If True, skip backup

    Returns:
        (backup_created, backup_path, total_files_backed_up)
    """
    if overwrite:
        return False, None, 0

    # Collect all file paths from all workspace_dirs
    all_files = []
    for files in all_files_by_workspace_dir.values():
        all_files.extend(files)

    # Find existing files that will be overwritten
    existing_files = [f for f in all_files if os.path.isfile(f)]

    if not existing_files:
        return False, None, 0

    # Create backup directory at final_path level
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{final_path}.backup.{timestamp}"

    try:
        os.makedirs(backup_dir, exist_ok=True)
        backed_up = 0

        for src_path in existing_files:
            # Calculate relative path from final_path to preserve directory structure
            rel_path = os.path.relpath(src_path, final_path)
            dst_path = os.path.join(backup_dir, rel_path)

            # Create parent dirs if needed
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            # Copy file
            shutil.copy2(src_path, dst_path)
            backed_up += 1
            logger.debug(f"Backed up: {src_path} -> {dst_path}")

        if backed_up > 0:
            logger.info(f"Backup created: {backup_dir} ({backed_up} files)")
            return True, backup_dir, backed_up

        # No files backed up, clean up empty dir
        os.rmdir(backup_dir)
        return False, None, 0

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise RuntimeError(f"Backup failed: {e}") from e


async def _process_workspace_dir(
    tool: str,
    workspace_dir: str,
    group: list[tuple[str, str]],  # [(subdir, display_name), ...]
    overwrite: bool,
    final_path: str,
) -> dict[str, int] | SetupStandardsError:
    """Process one workspace_dir: fetch trees + download all subdirs.

    Backup is already done at setup_standards level, so this function only handles
    fetching trees and downloading files.

    Uses "all or nothing" strategy: if ANY subdir fails to fetch, returns error.

    Returns:
        Dictionary mapping subdir to number of files downloaded
    """
    # PHASE 1: Fetch and validate ALL trees first (strict validation)
    trees = {}

    for subdir, display_name in group:
        gitlab_path = f"{GUIDELINES_BASE}/{tool}/{subdir}"
        tree = await Gitlab.get_repository_tree(gitlab_path)

        if not tree:
            # ANY failure → return error immediately (no partial success)
            return SetupStandardsError(
                error=f"GitLab error: No files in repository path '{gitlab_path}'"
            )

        trees[(subdir, display_name)] = tree

    # PHASE 2: Download files for each subdir
    os.makedirs(workspace_dir, exist_ok=True)
    results = {}

    for subdir, display_name in group:
        tree = trees[(subdir, display_name)]
        gitlab_path = f"{GUIDELINES_BASE}/{tool}/{subdir}"

        # Prepare download list for this subdir
        files = []
        for item in tree:
            if item["type"] == "blob":
                gitlab_file_path = item["path"]
                relative_path = _relative_path(gitlab_path, gitlab_file_path)
                workspace_path = os.path.join(workspace_dir, relative_path)
                files.append((item["path"], workspace_path))

        # Download in batches
        downloaded = 0
        for i in range(0, len(files), BATCH_SIZE):
            batch = files[i : i + BATCH_SIZE]
            batch_results = await asyncio.gather(
                *[_download_file(gp, wp) for gp, wp in batch],
                return_exceptions=True,
            )
            downloaded += sum(1 for r in batch_results if r is True)

        # Store downloaded count for this subdir
        results[subdir] = downloaded

    return results


async def _download_file(gitlab_path: str, workspace_path: str) -> bool:
    """Download single file using curl. Returns True on success."""
    try:
        os.makedirs(os.path.dirname(workspace_path), exist_ok=True)

        raw_url = Gitlab.get_raw_file_url(gitlab_path)

        cmd = [
            "curl",
            "-sf",
            "-H",
            f"Authorization: Bearer {Gitlab.TOKEN}",
            "-o",
            workspace_path,
            raw_url,
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            logger.warning(f"Failed download {gitlab_path}: {stderr.decode()}")
            return False

        return True

    except Exception as e:
        logger.warning(f"Error downloading {gitlab_path}: {e}")
        return False
