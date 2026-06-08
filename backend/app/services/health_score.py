from datetime import datetime

from app.schemas.analyze import RepositoryInfo, HealthScore, HealthScoreDimensions


class HealthScoreService:
    """Service for calculating repository health scores."""

    def calculate(self, repository: RepositoryInfo) -> HealthScore:
        """Calculate health score based on 4 dimensions (0-25 each, total 0-100)."""
        popularity = self._calculate_popularity(repository)
        activity = self._calculate_activity(repository)
        community = self._calculate_community(repository)
        maintenance = self._calculate_maintenance(repository)

        total_score = popularity + activity + community + maintenance

        return HealthScore(
            score=total_score,
            dimensions=HealthScoreDimensions(
                popularity=popularity,
                activity=activity,
                community=community,
                maintenance=maintenance,
            ),
        )

    def _calculate_popularity(self, repo: RepositoryInfo) -> int:
        """Calculate popularity score (0-25) based on stars."""
        stars = repo.stars
        if stars >= 100000:
            return 25
        elif stars >= 50000:
            return 20
        elif stars >= 10000:
            return 15
        elif stars >= 1000:
            return 10
        elif stars >= 100:
            return 5
        else:
            return min(stars, 5)

    def _calculate_activity(self, repo: RepositoryInfo) -> int:
        """Calculate activity score (0-25) based on recent updates."""
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(updated.tzinfo) - updated).days

            if days_since_update <= 7:
                return 25
            elif days_since_update <= 30:
                return 20
            elif days_since_update <= 90:
                return 15
            elif days_since_update <= 180:
                return 10
            elif days_since_update <= 365:
                return 5
            else:
                return 0
        except (ValueError, TypeError):
            return 10

    def _calculate_community(self, repo: RepositoryInfo) -> int:
        """Calculate community score (0-25) based on forks and watchers."""
        score = 0
        forks = repo.forks
        watchers = repo.watchers

        if forks >= 10000:
            score += 12
        elif forks >= 5000:
            score += 10
        elif forks >= 1000:
            score += 7
        elif forks >= 100:
            score += 4
        else:
            score += min(forks, 2) // 2

        if watchers >= 5000:
            score += 13
        elif watchers >= 1000:
            score += 10
        elif watchers >= 100:
            score += 5
        else:
            score += min(watchers, 3)

        return min(score, 25)

    def _calculate_maintenance(self, repo: RepositoryInfo) -> int:
        """Calculate maintenance score (0-25) based on issue ratio."""
        stars = repo.stars
        open_issues = repo.open_issues

        if stars == 0:
            return 10

        issue_ratio = open_issues / stars

        if issue_ratio <= 0.01:
            return 25
        elif issue_ratio <= 0.05:
            return 20
        elif issue_ratio <= 0.1:
            return 15
        elif issue_ratio <= 0.2:
            return 10
        elif issue_ratio <= 0.5:
            return 5
        else:
            return 0


health_score_service = HealthScoreService()