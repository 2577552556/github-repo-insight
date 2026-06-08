from app.clients.github import github_client
from app.schemas.analyze import RepositoryInfo, LanguageDistribution


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


github_service = GitHubService()