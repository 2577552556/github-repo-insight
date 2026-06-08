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
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an async HTTP request to the GitHub API."""
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
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


github_client = GitHubClient()