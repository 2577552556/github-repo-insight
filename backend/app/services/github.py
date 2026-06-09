from datetime import datetime, timedelta, timezone

from app.clients.github import github_client
from app.schemas.analyze import RepositoryInfo, LanguageDistribution, RepositoryMetrics


class GitHubService:
    """Service layer for GitHub API operations."""

    async def get_repository_info(self, owner: str, repo: str) -> RepositoryInfo:
        """Fetch and transform repository information."""
        data = await github_client.get_repository(owner, repo)
        return RepositoryInfo(
            name=data["name"],
            owner=data["owner"]["login"],
            full_name=data["full_name"],
            description=data.get("description"),
            html_url=data["html_url"],
            stars=data["stargazers_count"],
            forks=data["forks_count"],
            watchers=data["watchers_count"],
            open_issues=data["open_issues_count"],
            language=data.get("language"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            default_branch=data["default_branch"],
            license=data.get("license", {}).get("spdx_id") if data.get("license") else None,
            topics=data.get("topics", []),
        )

    async def get_language_distribution(self, owner: str, repo: str) -> LanguageDistribution:
        """Fetch languages and calculate percentages."""
        languages = await github_client.get_languages(owner, repo)
        total_bytes = sum(languages.values())
        if total_bytes == 0:
            return LanguageDistribution(languages={})
        percentages = {
            lang: round((bytes_count / total_bytes) * 100, 2)
            for lang, bytes_count in languages.items()
        }
        return LanguageDistribution(languages=percentages)

    async def get_contributors_count(self, owner: str, repo: str) -> int:
        """Fetch contributors count."""
        try:
            contributors = await github_client.get_contributors(owner, repo)
            return len(contributors)
        except Exception:
            return 0

    async def get_recent_commits_count(self, owner: str, repo: str, days: int = 30) -> int:
        """Fetch recent commits count within specified days."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            commits = await github_client.get_commits(owner, repo, since=since)
            return len(commits)
        except Exception:
            return 0

    async def get_repository_metrics(self, owner: str, repo: str, days: int = 90) -> RepositoryMetrics:
        """Fetch comprehensive repository metrics for scoring."""
        now = datetime.now(timezone.utc)
        since_30d = (now - timedelta(days=30)).isoformat()
        since_90d = (now - timedelta(days=days)).isoformat()

        # 并行获取数据
        commits_30d, commits_90d, contributors, issues, pulls, releases = await self._fetch_all_metrics(
            owner, repo, since_30d, since_90d
        )

        # 计算指标
        recent_commits_30d = len(commits_30d)
        recent_commits_90d = len(commits_90d)
        contributors_count = len(contributors)

        # Issues 统计
        open_issues_count = sum(1 for i in issues if i.get("state") == "open")
        closed_issues_30d = sum(
            1 for i in issues
            if i.get("state") == "closed"
            and i.get("closed_at")
            and i["closed_at"] >= since_30d
        )

        # PRs 统计
        open_prs_count = sum(1 for p in pulls if p.get("state") == "open")
        merged_prs_30d = sum(
            1 for p in pulls
            if p.get("merged_at") and p["merged_at"] >= since_30d
        )

        # Releases 统计
        releases_count = len(releases)
        latest_release_date = releases[0].get("published_at") if releases else None

        # 计算平均响应时间
        issue_response_time_avg = self._calculate_avg_response_time(issues)
        pr_merge_time_avg = self._calculate_avg_merge_time(pulls)

        return RepositoryMetrics(
            recent_commits_30d=recent_commits_30d,
            recent_commits_90d=recent_commits_90d,
            contributors_count=contributors_count,
            open_issues_count=open_issues_count,
            closed_issues_30d=closed_issues_30d,
            open_prs_count=open_prs_count,
            merged_prs_30d=merged_prs_30d,
            releases_count=releases_count,
            latest_release_date=latest_release_date,
            issue_response_time_avg=issue_response_time_avg,
            pr_merge_time_avg=pr_merge_time_avg,
        )

    async def _fetch_all_metrics(
        self, owner: str, repo: str, since_30d: str, since_90d: str
    ) -> tuple:
        """并行获取所有指标数据."""
        import asyncio

        # 使用 asyncio.gather 并行获取
        commits_30d, commits_90d, contributors, issues, pulls, releases = await asyncio.gather(
            github_client.get_commits(owner, repo, since=since_30d),
            github_client.get_commits(owner, repo, since=since_90d),
            github_client.get_contributors(owner, repo),
            github_client.get_issues(owner, repo, state="all", per_page=100),
            github_client.get_pulls(owner, repo, state="all", per_page=100),
            github_client.get_releases(owner, repo, per_page=30),
            return_exceptions=True,
        )

        # 处理异常情况
        commits_30d = commits_30d if isinstance(commits_30d, list) else []
        commits_90d = commits_90d if isinstance(commits_90d, list) else []
        contributors = contributors if isinstance(contributors, list) else []
        issues = issues if isinstance(issues, list) else []
        pulls = pulls if isinstance(pulls, list) else []
        releases = releases if isinstance(releases, list) else []

        return commits_30d, commits_90d, contributors, issues, pulls, releases

    def _calculate_avg_response_time(self, issues: list[dict]) -> float | None:
        """计算平均 Issue 响应时间（小时）."""
        response_times = []
        for issue in issues:
            if issue.get("state") == "closed" and issue.get("created_at") and issue.get("closed_at"):
                try:
                    created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
                    closed = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
                    response_time = (closed - created).total_seconds() / 3600
                    response_times.append(response_time)
                except (ValueError, TypeError):
                    continue

        if not response_times:
            return None

        return round(sum(response_times) / len(response_times), 2)

    def _calculate_avg_merge_time(self, pulls: list[dict]) -> float | None:
        """计算平均 PR 合并时间（小时）."""
        merge_times = []
        for pr in pulls:
            if pr.get("merged_at") and pr.get("created_at"):
                try:
                    created = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                    merged = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
                    merge_time = (merged - created).total_seconds() / 3600
                    merge_times.append(merge_time)
                except (ValueError, TypeError):
                    continue

        if not merge_times:
            return None

        return round(sum(merge_times) / len(merge_times), 2)


github_service = GitHubService()