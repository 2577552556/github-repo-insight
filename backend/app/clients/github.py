import json
from pathlib import Path

import httpx

from app.core.config import settings
from app.core.exceptions import (
    GitHubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
    NetworkError,
)


class GitHubClient:
    """Async GitHub API client using httpx."""

    def __init__(self):
        self.base_url = settings.GITHUB_API_URL
        self.timeout = settings.timeout

    def _get_headers(self) -> dict:
        """动态构建请求头，确保运行时token更新立即生效"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        # 优先从 settings.json 读取 token（支持运行时更新），否则 fallback 到 settings 对象
        token = self._load_token_from_file() or settings.GITHUB_TOKEN
        if token:
            headers["Authorization"] = f"token {token}"
        return headers

    def _load_token_from_file(self) -> str | None:
        """从 settings.json 加载 token"""
        settings_file = Path(__file__).parent.parent.parent / "data" / "settings.json"
        if settings_file.exists():
            data = json.loads(settings_file.read_text(encoding="utf-8"))
            return data.get("github_token")
        return None

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an async HTTP request to the GitHub API."""
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs,
                )
                if response.status_code == 404:
                    raise RepositoryNotFoundError()
                elif response.status_code == 403:
                    raise RateLimitError()
                elif response.status_code >= 400:
                    raise GitHubAPIError(f"GitHub API error: {response.status_code}")
                return response.json()
            except httpx.TimeoutException:
                raise NetworkError("Request to GitHub API timed out")
            except httpx.RequestError as e:
                raise NetworkError(f"Network error: {str(e)}")

    async def get_repository(self, owner: str, repo: str) -> dict:
        """Fetch repository metadata."""
        return await self._request("GET", f"/repos/{owner}/{repo}")

    async def get_languages(self, owner: str, repo: str) -> dict[str, int]:
        """Fetch repository languages (byte counts)."""
        return await self._request("GET", f"/repos/{owner}/{repo}/languages")

    async def get_contributors(self, owner: str, repo: str) -> list[dict]:
        """Fetch repository contributors."""
        return await self._request("GET", f"/repos/{owner}/{repo}/contributors")

    async def get_commits(
        self, owner: str, repo: str, since: str | None = None, until: str | None = None
    ) -> list[dict]:
        """Fetch repository commits with optional date range."""
        params = {}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return await self._request("GET", f"/repos/{owner}/{repo}/commits", params=params)

    async def get_issues(
        self, owner: str, repo: str, state: str = "all", per_page: int = 100
    ) -> list[dict]:
        """Fetch repository issues."""
        return await self._request(
            "GET", f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page, "sort": "updated"}
        )

    async def get_readme(self, owner: str, repo: str) -> dict:
        """Fetch repository README."""
        return await self._request("GET", f"/repos/{owner}/{repo}/readme")

    async def get_topics(self, owner: str, repo: str) -> list[str]:
        """Fetch repository topics."""
        data = await self._request("GET", f"/repos/{owner}/{repo}/topics")
        return data.get("names", [])

    async def get_pulls(
        self, owner: str, repo: str, state: str = "all", per_page: int = 100
    ) -> list[dict]:
        """Fetch repository pull requests."""
        return await self._request(
            "GET", f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": per_page, "sort": "updated"}
        )

    async def get_releases(self, owner: str, repo: str, per_page: int = 30) -> list[dict]:
        """Fetch repository releases."""
        return await self._request(
            "GET", f"/repos/{owner}/{repo}/releases",
            params={"per_page": per_page}
        )


github_client = GitHubClient()