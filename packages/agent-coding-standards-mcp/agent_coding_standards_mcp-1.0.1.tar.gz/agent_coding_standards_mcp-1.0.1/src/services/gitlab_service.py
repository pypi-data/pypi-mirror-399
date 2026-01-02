"""GitLab API service for repository operations."""

from typing import cast
from urllib.parse import quote

import httpx

from src.server_settings import settings


class Gitlab:
    """Static GitLab API client using cached configuration."""

    # --- Load settings ONCE at class import ---
    DOMAIN = settings.GITLAB_URL.rstrip("/")
    TOKEN = settings.GITLAB_TOKEN
    PROJECT = quote(settings.GITLAB_PROJECT_PATH, safe="")
    BRANCH = settings.GITLAB_BRANCH

    @staticmethod
    def _api_base_url() -> str:
        """Construct the base API URL for GitLab."""
        return f"{Gitlab.DOMAIN}/api/v4"

    @staticmethod
    def _headers() -> dict[str, str]:
        """Construct headers for GitLab API requests."""
        return {
            "Authorization": f"Bearer {Gitlab.TOKEN}",
            "Accept": "application/json",
        }

    @staticmethod
    async def get_repository_tree(path: str = "guidelines") -> list[dict[str, str]]:
        """Fetch the repository tree from GitLab for the specified path."""
        url = (
            f"{Gitlab._api_base_url()}/projects/{Gitlab.PROJECT}/repository/tree"
            f"?ref={Gitlab.BRANCH}&recursive=true&per_page=100"
        )

        if path and path != ".":
            url += f"&path={quote(path)}"

        async with httpx.AsyncClient(headers=Gitlab._headers()) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        return cast(list[dict[str, str]], resp.json())

    @staticmethod
    def get_raw_file_url(file_path: str) -> str:
        """Get the raw file URL for direct download."""
        return (
            f"{Gitlab._api_base_url()}/projects/{Gitlab.PROJECT}/repository/files/{quote(file_path, safe='')}/raw"
            f"?ref={Gitlab.BRANCH}"
        )
