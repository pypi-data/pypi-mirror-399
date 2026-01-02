"""Unit tests for setup_standards.py"""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.models import (
    SetupStandardsError,
    SetupStandardsResponse,
)
from src.tools.setup_standards import setup_standards

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_gitlab():
    """Mock GitLab service with common methods."""
    with patch("src.tools.setup_standards.Gitlab") as mock:
        mock.TOKEN = "test-token-123"
        mock.get_repository_tree = AsyncMock()
        mock.get_raw_file_url = MagicMock(
            return_value="https://gitlab.example.com/api/v4/projects/test/files/raw"
        )
        yield mock


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture
def mock_subprocess():
    """Mock asyncio subprocess for file downloads."""
    with patch("asyncio.create_subprocess_exec") as mock_proc:
        process_mock = AsyncMock()
        process_mock.communicate = AsyncMock(return_value=(b"", b""))
        process_mock.returncode = 0
        mock_proc.return_value = process_mock
        yield mock_proc


@pytest.fixture
def mock_cline_tree():
    """Mock tree response for cline tool (rules + workflows subdirs)."""

    def get_tree(path):
        if "rules" in path:
            return [
                {"type": "blob", "path": f"{path}/rule1.md"},
                {"type": "blob", "path": f"{path}/rule2.md"},
                {"type": "blob", "path": f"{path}/rule3.md"},
            ]
        elif "workflows" in path:
            return [
                {"type": "blob", "path": f"{path}/workflow1.md"},
                {"type": "blob", "path": f"{path}/workflow2.md"},
            ]
        return []

    return get_tree


# ============================================================================
# GROUP 1: INPUT VALIDATION TESTS
# ============================================================================


@pytest.mark.unit
class TestInputValidation:
    """Test input validation for setup_standards function."""

    @pytest.mark.asyncio
    async def test_global_scope_valid_tool(
        self, mock_gitlab, mock_subprocess, mock_cline_tree
    ):
        """Global scope with valid agent."""
        # Arrange
        mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

        with patch("src.tools.setup_standards.get_global_download_path") as mock_path:
            mock_path.return_value = "~/Documents/Cline"
            with patch("os.makedirs"), patch("os.path.exists", return_value=False):
                # Act
                result = await setup_standards("cline", is_scope_global=True)

                # Assert
                assert isinstance(result, SetupStandardsResponse)
                assert "Documents/Cline" in result.downloaded_to
                assert "rules" in result.downloaded_files
                assert "workflows" in result.downloaded_files
                assert result.downloaded_files["rules"] == 3
                assert result.downloaded_files["workflows"] == 2

    @pytest.mark.asyncio
    async def test_global_scope_invalid_tool(self, mock_gitlab):
        """Global scope with invalid agent."""
        # Arrange
        with patch("src.tools.setup_standards.get_global_download_path") as mock_path:
            mock_path.return_value = None

            # Act
            result = await setup_standards("invalid_tool", is_scope_global=True)

            # Assert
            assert isinstance(result, SetupStandardsError)
            assert "No global path" in result.error
            assert "invalid_tool" in result.error

    @pytest.mark.asyncio
    async def test_workspace_scope_missing_workspace_path(self):
        """Workspace scope without workspace_path."""
        # Act
        result = await setup_standards(
            "cline", is_scope_global=False, workspace_path=None
        )

        # Assert
        assert isinstance(result, SetupStandardsError)
        assert "workspace_path required" in result.error

    @pytest.mark.asyncio
    async def test_workspace_scope_relative_path(self):
        """Workspace scope with relative path (should fail)."""
        # Act
        result = await setup_standards(
            "cline", is_scope_global=False, workspace_path="relative/path"
        )

        # Assert
        assert isinstance(result, SetupStandardsError)
        assert "must be absolute path" in result.error

    @pytest.mark.asyncio
    async def test_workspace_scope_valid_absolute_path(
        self, mock_gitlab, mock_subprocess, temp_dir, mock_cline_tree
    ):
        """Workspace scope with valid absolute path."""
        # Arrange
        mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline", is_scope_global=False, workspace_path=temp_dir
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert temp_dir in result.downloaded_to
            assert ".cline" in result.downloaded_to
            assert "rules" in result.downloaded_files
            assert "workflows" in result.downloaded_files


# ============================================================================
# GROUP 2: GITLAB INTEGRATION TESTS
# ============================================================================


@pytest.mark.unit
class TestGitlabIntegration:
    """Test GitLab API integration scenarios."""

    @pytest.mark.asyncio
    async def test_gitlab_returns_empty_tree(self, mock_gitlab, temp_dir):
        """GitLab returns empty tree."""
        # Arrange
        mock_gitlab.get_repository_tree.return_value = []

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline", is_scope_global=False, workspace_path=temp_dir
            )

            # Assert
            assert isinstance(result, SetupStandardsError)
            assert "No files in" in result.error

    @pytest.mark.asyncio
    async def test_gitlab_returns_none(self, mock_gitlab, temp_dir):
        """GitLab API error (returns None)."""
        # Arrange
        mock_gitlab.get_repository_tree.return_value = None

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline", is_scope_global=False, workspace_path=temp_dir
            )

            # Assert
            assert isinstance(result, SetupStandardsError)
            assert "No files in" in result.error

    @pytest.mark.asyncio
    async def test_gitlab_mixed_files_and_directories(
        self, mock_gitlab, mock_subprocess, temp_dir
    ):
        """GitLab returns mixed files and directories (should only download blobs)."""

        # Arrange
        def get_tree(path):
            if "rules" in path:
                return [
                    {"type": "blob", "path": f"{path}/rule1.md"},
                    {"type": "tree", "path": f"{path}/subdir"},  # Should be ignored
                    {"type": "blob", "path": f"{path}/rule2.md"},
                    {"type": "blob", "path": f"{path}/rule3.md"},
                ]
            elif "workflows" in path:
                return [
                    {"type": "blob", "path": f"{path}/wf1.md"},
                    {"type": "tree", "path": f"{path}/nested"},  # Should be ignored
                    {"type": "blob", "path": f"{path}/wf2.md"},
                ]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline", is_scope_global=False, workspace_path=temp_dir
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            # Should only count blobs (3 in rules, 2 in workflows)
            assert result.downloaded_files["rules"] == 3
            assert result.downloaded_files["workflows"] == 2

    @pytest.mark.asyncio
    async def test_multiple_subdirectories(
        self, mock_gitlab, mock_subprocess, temp_dir, mock_cline_tree
    ):
        """Multiple subdirectories (rules + workflows)."""
        # Arrange
        mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline", is_scope_global=False, workspace_path=temp_dir
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert "rules" in result.downloaded_files
            assert "workflows" in result.downloaded_files
            assert result.downloaded_files["rules"] == 3
            assert result.downloaded_files["workflows"] == 2


# ============================================================================
# GROUP 3: BACKUP HANDLING TESTS
# ============================================================================


@pytest.mark.unit
class TestBackupHandling:
    """Test backup creation with file-level conflict detection."""

    @pytest.mark.asyncio
    async def test_no_backup_when_overwrite_true(
        self, mock_gitlab, mock_subprocess, temp_dir, mock_cline_tree
    ):
        """overwrite=True -> no backup even if files exist."""
        # Arrange
        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Create existing files
            target_dir = os.path.join(temp_dir, ".cline", "rules")
            os.makedirs(target_dir, exist_ok=True)
            Path(os.path.join(target_dir, "rule1.md")).write_text("old content")
            Path(os.path.join(target_dir, "rule2.md")).write_text("old content")

            mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

            # Act
            result = await setup_standards(
                "cline",
                is_scope_global=False,
                workspace_path=temp_dir,
                overwrite=True,  # Key: overwrite=True
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert result.backup_info is None

    @pytest.mark.asyncio
    async def test_no_backup_when_no_conflicts(
        self, mock_gitlab, mock_subprocess, temp_dir, mock_cline_tree
    ):
        """overwrite=False but no existing files -> no backup."""
        # Arrange
        mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Don't create any existing files
            # Act
            result = await setup_standards(
                "cline",
                is_scope_global=False,
                workspace_path=temp_dir,
                overwrite=False,
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert result.backup_info is None

    @pytest.mark.asyncio
    async def test_backup_only_conflicting_files(
        self, mock_gitlab, mock_subprocess, temp_dir, mock_cline_tree
    ):
        """overwrite=False + some existing files -> backup only those."""
        # Arrange
        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Create ONLY rule1.md and rule3.md (not rule2.md)
            target_dir = os.path.join(temp_dir, ".cline", "rules")
            os.makedirs(target_dir, exist_ok=True)
            Path(os.path.join(target_dir, "rule1.md")).write_text("old rule1")
            Path(os.path.join(target_dir, "rule3.md")).write_text("old rule3")
            # rule2.md does NOT exist

            mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

            # Act - download rule1, rule2, rule3
            result = await setup_standards(
                "cline",
                is_scope_global=False,
                workspace_path=temp_dir,
                overwrite=False,
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert result.backup_info is not None
            assert result.backup_info.file_count == 2  # Only rule1 + rule3
            assert result.backup_info.backup_dir is not None

            # Verify backup contains only conflicting files (backup at final_path level)
            backup_dir = result.backup_info.backup_dir
            # Backup path should be at final_path level, not workspace_dir level
            assert temp_dir in backup_dir
            assert ".cline.backup" in backup_dir
            # Files should be relative to final_path
            assert os.path.exists(os.path.join(backup_dir, "rules", "rule1.md"))
            assert os.path.exists(os.path.join(backup_dir, "rules", "rule3.md"))
            assert not os.path.exists(os.path.join(backup_dir, "rules", "rule2.md"))

    @pytest.mark.asyncio
    async def test_backup_preserves_directory_structure(
        self, mock_gitlab, mock_subprocess, temp_dir
    ):
        """Backup maintains nested directory structure from GitLab."""

        # Arrange - Mock GitLab tree with nested paths
        def get_tree_with_nested_paths(path):
            if "skills" in path:
                return [
                    {
                        "type": "blob",
                        "path": f"{path}/backend-development/SKILL.md",
                    },
                ]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree_with_nested_paths

        with patch("src.tools.setup_standards.get_subdirs") as mock_subdirs:
            mock_subdirs.return_value = {"skills": "skills"}
            with patch(
                "src.tools.setup_standards.get_workspace_download_dir"
            ) as mock_dir:
                mock_dir.return_value = "/.claude"

                # Create existing file at nested path
                target_dir = os.path.join(
                    temp_dir, ".claude", "skills", "backend-development"
                )
                os.makedirs(target_dir, exist_ok=True)
                Path(os.path.join(target_dir, "SKILL.md")).write_text("old content")

                # Act
                result = await setup_standards(
                    "claude",
                    is_scope_global=False,
                    workspace_path=temp_dir,
                    overwrite=False,
                )

                # Assert
                assert isinstance(result, SetupStandardsResponse)
                assert result.backup_info is not None
                backup_dir = result.backup_info.backup_dir
                # Backup path should be at final_path level
                assert temp_dir in backup_dir
                assert ".claude.backup" in backup_dir
                # Verify backup maintains nested structure (relative to final_path)
                assert os.path.exists(
                    os.path.join(
                        backup_dir, "skills", "backend-development", "SKILL.md"
                    )
                )
                # Verify backup does NOT flatten to root
                assert not os.path.exists(os.path.join(backup_dir, "SKILL.md"))
                assert not os.path.exists(
                    os.path.join(backup_dir, "backend-development", "SKILL.md")
                )

    @pytest.mark.asyncio
    async def test_shared_backup_for_same_final_path(
        self, mock_gitlab, mock_subprocess, temp_dir
    ):
        """Subdirs sharing the same final_path share the same backup."""

        # Arrange
        def get_tree(path):
            if "rules" in path:
                return [{"type": "blob", "path": f"{path}/rule.md"}]
            elif "workflows" in path:
                return [{"type": "blob", "path": f"{path}/workflow.md"}]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Create existing files in DIFFERENT directories
            rules_dir = os.path.join(temp_dir, ".cline", "rules")
            workflows_dir = os.path.join(temp_dir, ".cline", "workflows")

            os.makedirs(rules_dir, exist_ok=True)
            os.makedirs(workflows_dir, exist_ok=True)

            Path(os.path.join(rules_dir, "rule.md")).write_text("old rule")
            Path(os.path.join(workflows_dir, "workflow.md")).write_text("old workflow")

            # Act
            result = await setup_standards(
                "cline",
                is_scope_global=False,
                workspace_path=temp_dir,
                overwrite=False,
            )

            # Assert - Both subdirs share the same backup (same final_path)
            assert isinstance(result, SetupStandardsResponse)
            assert result.backup_info is not None
            assert (
                result.backup_info.file_count == 2
            )  # 2 files total (rule.md + workflow.md)

            # Same backup directory (backup at final_path level)
            backup_dir = result.backup_info.backup_dir
            # Backup should be at final_path level, not workspace_dir level
            assert temp_dir in backup_dir
            assert ".cline.backup" in backup_dir

            # Verify backup contents with relative paths from final_path
            assert os.path.exists(os.path.join(backup_dir, "rules", "rule.md"))
            assert os.path.exists(os.path.join(backup_dir, "workflows", "workflow.md"))

    @pytest.mark.asyncio
    async def test_backup_failure_raises_error(self, mock_gitlab, temp_dir):
        """Backup fails -> RuntimeError propagates."""

        # Arrange
        def get_tree(path):
            if "rules" in path:
                return [{"type": "blob", "path": f"{path}/file.md"}]
            elif "workflows" in path:  # ✅ FIXED: Mock both subdirs
                return [{"type": "blob", "path": f"{path}/wf.md"}]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Create existing file
            target_dir = os.path.join(temp_dir, ".cline", "rules")
            os.makedirs(target_dir, exist_ok=True)
            Path(os.path.join(target_dir, "file.md")).write_text("old")

            # Mock shutil.copy2 to fail
            with patch("shutil.copy2") as mock_copy:
                mock_copy.side_effect = PermissionError("Access denied")

                # Act & Assert
                result = await setup_standards(
                    "cline",
                    is_scope_global=False,
                    workspace_path=temp_dir,
                    overwrite=False,
                )

                assert isinstance(result, SetupStandardsError)
                assert "Backup failed" in result.error

    @pytest.mark.asyncio
    async def test_partial_failure_returns_error(self, mock_gitlab, temp_dir):
        """If ANY subdir fails to fetch, entire operation fails (all or nothing)."""

        # Arrange - rules succeeds, workflows fails
        def get_tree(path):
            if "rules" in path:
                return [{"type": "blob", "path": f"{path}/rule.md"}]
            elif "workflows" in path:
                return None  # Fails
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline",
                is_scope_global=False,
                workspace_path=temp_dir,
                overwrite=False,
            )

            # Assert - Should return error, NOT partial success
            assert isinstance(result, SetupStandardsError)
            assert "No files in repository path" in result.error
            assert "workflows" in result.error


# ============================================================================
# GROUP 4: FILE DOWNLOAD TESTS
# ============================================================================


@pytest.mark.unit
class TestFileDownload:
    """Test file download functionality."""

    @pytest.mark.asyncio
    async def test_all_files_download_successfully(
        self, mock_gitlab, mock_subprocess, temp_dir, mock_cline_tree
    ):
        """All files download successfully."""
        # Arrange
        mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline", is_scope_global=False, workspace_path=temp_dir
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert result.downloaded_files["rules"] == 3
            assert result.downloaded_files["workflows"] == 2
            # No backup when overwrite=True (default)
            assert result.backup_info is None

    @pytest.mark.asyncio
    async def test_some_files_fail_to_download(self, mock_gitlab, temp_dir):
        """Some files fail to download."""
        # Arrange
        call_count = 0

        def get_tree(path):
            if "rules" in path:
                return [
                    {"type": "blob", "path": f"{path}/file1.md"},
                    {"type": "blob", "path": f"{path}/file2.md"},
                    {"type": "blob", "path": f"{path}/file3.md"},
                ]
            elif "workflows" in path:
                return [{"type": "blob", "path": f"{path}/wf1.md"}]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        async def mock_subprocess_with_failures(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            process = AsyncMock()
            # Fail on 2nd call (file2.md in rules)
            process.communicate = AsyncMock(
                return_value=(b"", b"Error" if call_count == 2 else b"")
            )
            process.returncode = 1 if call_count == 2 else 0
            return process

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"
            with patch(
                "asyncio.create_subprocess_exec",
                side_effect=mock_subprocess_with_failures,
            ):
                # Act
                result = await setup_standards(
                    "cline", is_scope_global=False, workspace_path=temp_dir
                )

                # Assert
                assert isinstance(result, SetupStandardsResponse)
                # Should have 2 successful downloads in rules (file1, file3)
                assert result.downloaded_files["rules"] == 2
                assert result.downloaded_files["workflows"] == 1

    @pytest.mark.asyncio
    async def test_all_files_fail_to_download(self, mock_gitlab, temp_dir):
        """All files fail to download."""

        # Arrange
        def get_tree(path):
            if "rules" in path:
                return [{"type": "blob", "path": f"{path}/file1.md"}]
            elif "workflows" in path:
                return [{"type": "blob", "path": f"{path}/wf1.md"}]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        async def mock_subprocess_fail(*args, **kwargs):
            process = AsyncMock()
            process.communicate = AsyncMock(return_value=(b"", b"Network error"))
            process.returncode = 1
            return process

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"
            with patch(
                "asyncio.create_subprocess_exec", side_effect=mock_subprocess_fail
            ):
                # Act
                result = await setup_standards(
                    "cline", is_scope_global=False, workspace_path=temp_dir
                )

                # Assert
                assert isinstance(result, SetupStandardsResponse)
                # All downloads fail in both subdirectories
                assert result.downloaded_files["rules"] == 0
                assert result.downloaded_files["workflows"] == 0

    @pytest.mark.asyncio
    async def test_batch_download_large_files(
        self, mock_gitlab, mock_subprocess, temp_dir
    ):
        """Batch download (>5 files) - tests batching logic."""

        # Arrange - Create 12 files to test BATCH_SIZE=5
        def get_tree(path):
            if "rules" in path:
                return [
                    {"type": "blob", "path": f"{path}/file{i}.md"} for i in range(12)
                ]
            elif "workflows" in path:
                return [{"type": "blob", "path": f"{path}/wf1.md"}]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Act
            result = await setup_standards(
                "cline", is_scope_global=False, workspace_path=temp_dir
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert result.downloaded_files["rules"] == 12
            # Verify batching occurred (12 files + 1 workflow = 13 calls)
            assert mock_subprocess.call_count == 13

    @pytest.mark.asyncio
    async def test_network_timeout_during_download(self, mock_gitlab, temp_dir):
        """Network timeout during download."""

        # Arrange
        def get_tree(path):
            if "rules" in path:
                return [
                    {"type": "blob", "path": f"{path}/file1.md"},
                    {"type": "blob", "path": f"{path}/file2.md"},
                ]
            elif "workflows" in path:
                return [{"type": "blob", "path": f"{path}/wf1.md"}]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree

        async def mock_subprocess_timeout(*args, **kwargs):
            raise TimeoutError("Connection timeout")

        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"
            with patch(
                "asyncio.create_subprocess_exec", side_effect=mock_subprocess_timeout
            ):
                # Act
                result = await setup_standards(
                    "cline", is_scope_global=False, workspace_path=temp_dir
                )

                # Assert - Should handle exception gracefully
                assert isinstance(result, SetupStandardsResponse)
                assert result.downloaded_files["rules"] == 0
                assert result.downloaded_files["workflows"] == 0

    @pytest.mark.asyncio
    async def test_download_with_backup(
        self, mock_gitlab, mock_subprocess, temp_dir, mock_cline_tree
    ):
        """Download files with backup when overwrite=False."""
        # Arrange
        with patch("src.tools.setup_standards.get_workspace_download_dir") as mock_dir:
            mock_dir.return_value = "/.cline"

            # Create existing files
            target_dir = os.path.join(temp_dir, ".cline", "rules")
            os.makedirs(target_dir, exist_ok=True)
            Path(os.path.join(target_dir, "rule1.md")).write_text("old")

            mock_gitlab.get_repository_tree.side_effect = mock_cline_tree

            # Act
            result = await setup_standards(
                "cline",
                is_scope_global=False,
                workspace_path=temp_dir,
                overwrite=False,  # Backup enabled
            )

            # Assert
            assert isinstance(result, SetupStandardsResponse)
            assert result.downloaded_files["rules"] == 3  # Downloaded
            assert result.backup_info is not None  # Backup created
            assert result.backup_info.file_count == 1  # Only rule1.md
            assert result.backup_info.backup_dir is not None

    @pytest.mark.asyncio
    async def test_download_preserves_nested_structure_from_gitlab(
        self, mock_gitlab, temp_dir
    ):
        """Download preserves nested directory structure from GitLab repository."""

        # Arrange - Mock GitLab tree with nested paths
        def get_tree_with_nested_paths(path):
            if "skills" in path:
                return [
                    {
                        "type": "blob",
                        "path": f"{path}/backend-development/SKILL.md",
                    },
                    {
                        "type": "blob",
                        "path": f"{path}/backend-development/references/backend-api-design.md",
                    },
                ]
            return []

        mock_gitlab.get_repository_tree.side_effect = get_tree_with_nested_paths

        # Mock subprocess to actually create files
        async def mock_subprocess_create_files(*args, **kwargs):
            # asyncio.create_subprocess_exec is called with unpacked args: create_subprocess_exec('curl', '-sf', '-H', ..., '-o', workspace_path, raw_url)
            # So args is a tuple of individual command arguments
            if len(args) >= 6 and args[0] == "curl" and args[4] == "-o":
                workspace_path = args[5]
                # Create directory if needed
                os.makedirs(os.path.dirname(workspace_path), exist_ok=True)
                # Create empty file
                Path(workspace_path).write_text("")

            process = AsyncMock()
            process.communicate = AsyncMock(return_value=(b"", b""))
            process.returncode = 0
            return process

        with patch("src.tools.setup_standards.get_subdirs") as mock_subdirs:
            mock_subdirs.return_value = {"skills": "skills"}
            with patch(
                "src.tools.setup_standards.get_workspace_download_dir"
            ) as mock_dir:
                mock_dir.return_value = "/.claude"
                with patch(
                    "asyncio.create_subprocess_exec",
                    side_effect=mock_subprocess_create_files,
                ):
                    # Act
                    result = await setup_standards(
                        "claude",
                        is_scope_global=False,
                        workspace_path=temp_dir,
                    )

                    # Assert
                    assert isinstance(result, SetupStandardsResponse)
                    assert result.downloaded_files["skills"] == 2

                    # Verify files are saved with nested structure
                    skills_dir = os.path.join(temp_dir, ".claude", "skills")
                    assert os.path.exists(
                        os.path.join(skills_dir, "backend-development", "SKILL.md")
                    )
                    assert os.path.exists(
                        os.path.join(
                            skills_dir,
                            "backend-development",
                            "references",
                            "backend-api-design.md",
                        )
                    )

                    # Verify files are NOT flattened to root
                    assert not os.path.exists(os.path.join(skills_dir, "SKILL.md"))
                    assert not os.path.exists(
                        os.path.join(skills_dir, "backend-api-design.md")
                    )
