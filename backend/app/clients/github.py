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
        # 从 settings_service 获取解密后的 token
        from app.services.settings_service import settings_service
        token = settings_service.get_decrypted_github_token() or settings.GITHUB_TOKEN
        if token:
            headers["Authorization"] = f"token {token}"
        return headers

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

    def _has_next_page(self, response: httpx.Response) -> bool:
        """检查响应是否有下一页"""
        link_header = response.headers.get("Link", "")
        if not link_header:
            return False
        return 'rel="next"' in link_header

    async def _fetch_all_pages(self, method: str, path: str, params: dict, max_pages: int = 10) -> list:
        """循环获取所有分页数据"""
        results = []
        page = 1
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while page <= max_pages:
                page_params = {**params, "page": page}
                url = f"{self.base_url}{path}"
                headers = self._get_headers()
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=page_params,
                    )
                    if response.status_code == 404:
                        raise RepositoryNotFoundError()
                    elif response.status_code == 403:
                        raise RateLimitError()
                    elif response.status_code >= 400:
                        raise GitHubAPIError(f"GitHub API error: {response.status_code}")

                    data = response.json()
                    if not data:
                        break
                    results.extend(data)
                    # 检查是否还有下一页
                    if not self._has_next_page(response):
                        break
                    page += 1
                except httpx.TimeoutException:
                    raise NetworkError("Request to GitHub API timed out")
                except httpx.RequestError as e:
                    raise NetworkError(f"Network error: {str(e)}")
        return results

    async def get_repository(self, owner: str, repo: str) -> dict:
        """Fetch repository metadata."""
        return await self._request("GET", f"/repos/{owner}/{repo}")

    async def get_languages(self, owner: str, repo: str) -> dict[str, int]:
        """Fetch repository languages (byte counts)."""
        return await self._request("GET", f"/repos/{owner}/{repo}/languages")

    async def get_contributors(self, owner: str, repo: str) -> list[dict]:
        """Fetch repository contributors (with pagination)."""
        return await self._fetch_all_pages(
            "GET",
            f"/repos/{owner}/{repo}/contributors",
            params={"per_page": 100}
        )

    async def get_commits(
        self, owner: str, repo: str, since: str | None = None, until: str | None = None
    ) -> list[dict]:
        """Fetch repository commits with optional date range (with pagination)."""
        params = {"per_page": 100}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return await self._fetch_all_pages(
            "GET",
            f"/repos/{owner}/{repo}/commits",
            params=params
        )

    async def get_issues(
        self, owner: str, repo: str, state: str = "all", per_page: int = 100
    ) -> list[dict]:
        """Fetch repository issues (with pagination)."""
        return await self._fetch_all_pages(
            "GET",
            f"/repos/{owner}/{repo}/issues",
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
        """Fetch repository pull requests (with pagination)."""
        return await self._fetch_all_pages(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": per_page}
        )

    async def get_releases(self, owner: str, repo: str, per_page: int = 30) -> list[dict]:
        """Fetch repository releases (with pagination)."""
        return await self._fetch_all_pages(
            "GET",
            f"/repos/{owner}/{repo}/releases",
            params={"per_page": per_page}
        )


github_client = GitHubClient()