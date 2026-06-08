from datetime import datetime

from app.schemas.analyze import RepositoryInfo, HealthScore, HealthScoreDimensions


class HealthScoreService:
    """Service for calculating repository health scores (0-100).

    评分维度：
    - Popularity (25%): Stars/Forks/Watchers
    - Activity (30%): 更新频率/Commit频率
    - Community (20%): Contributors/Issues
    - Engineering (15%): License/README/Topics
    - Maintenance (10%): 维护风险
    """

    def calculate(
        self,
        repository: RepositoryInfo,
        recent_commits: int = 0,
        contributors_count: int = 0,
    ) -> HealthScore:
        """Calculate health score based on 5 dimensions."""
        popularity = self._calculate_popularity(repository)
        activity = self._calculate_activity(repository, recent_commits)
        community = self._calculate_community(repository, contributors_count)
        engineering = self._calculate_engineering(repository)
        maintenance = self._calculate_maintenance(repository, recent_commits, contributors_count)

        total_score = popularity + activity + community + engineering + maintenance

        return HealthScore(
            score=total_score,
            dimensions=HealthScoreDimensions(
                popularity=popularity,
                activity=activity,
                community=community,
                engineering=engineering,
                maintenance=maintenance,
            ),
        )

    def _calculate_popularity(self, repo: RepositoryInfo) -> int:
        """计算流行度 (0-25)

        Stars: <100=1, <1k=5, <10k=10, <50k=15, <100k=20, >=100k=25
        Forks: 额外加分
        Watchers: 额外加分
        """
        stars = repo.stars
        score = 0

        # Stars 评分
        if stars >= 100000:
            score += 15
        elif stars >= 50000:
            score += 12
        elif stars >= 10000:
            score += 9
        elif stars >= 1000:
            score += 5
        elif stars >= 100:
            score += 2
        else:
            score += 1

        # Forks 加分 (反映实际使用)
        forks = repo.forks
        if forks >= 10000:
            score += 5
        elif forks >= 5000:
            score += 4
        elif forks >= 1000:
            score += 3
        elif forks >= 100:
            score += 2
        elif forks > 0:
            score += 1

        # Watchers 加分
        watchers = repo.watchers
        if watchers >= 5000:
            score += 5
        elif watchers >= 1000:
            score += 3
        elif watchers >= 100:
            score += 1

        return min(score, 25)

    def _calculate_activity(self, repo: RepositoryInfo, recent_commits: int) -> int:
        """计算活跃度 (0-30)

        基于：更新时间 + 近期 Commit 数量
        """
        score = 0

        # 更新时间评分 (0-15)
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(updated.tzinfo) - updated).days

            if days_since_update <= 7:
                score += 15
            elif days_since_update <= 30:
                score += 12
            elif days_since_update <= 90:
                score += 8
            elif days_since_update <= 180:
                score += 4
            elif days_since_update <= 365:
                score += 2
            else:
                score += 0
        except (ValueError, TypeError):
            score += 5  # 默认中等

        # Commit 频率评分 (0-15)
        if recent_commits >= 100:
            score += 15
        elif recent_commits >= 50:
            score += 12
        elif recent_commits >= 20:
            score += 9
        elif recent_commits >= 10:
            score += 6
        elif recent_commits >= 5:
            score += 3
        elif recent_commits > 0:
            score += 1
        # 0 commits 得 0 分

        return min(score, 30)

    def _calculate_community(self, repo: RepositoryInfo, contributors_count: int) -> int:
        """计算社区活跃度 (0-20)

        基于：Contributors 数量 + Issue 处理情况
        """
        score = 0

        # Contributors 评分 (0-12)
        if contributors_count >= 100:
            score += 12
        elif contributors_count >= 50:
            score += 10
        elif contributors_count >= 20:
            score += 8
        elif contributors_count >= 10:
            score += 6
        elif contributors_count >= 5:
            score += 4
        elif contributors_count >= 2:
            score += 2
        else:
            score += 1  # 只有 1 个贡献者

        # Issue 比率评分 (0-8)
        # 低 Issue 比率意味着维护良好
        stars = max(repo.stars, 1)
        open_issues = repo.open_issues
        issue_ratio = open_issues / stars

        if issue_ratio <= 0.01:  # 几乎没有 open issues
            score += 8
        elif issue_ratio <= 0.05:
            score += 6
        elif issue_ratio <= 0.1:
            score += 4
        elif issue_ratio <= 0.2:
            score += 2
        else:  # issue 过多
            score += 0

        return min(score, 20)

    def _calculate_engineering(self, repo: RepositoryInfo) -> int:
        """计算工程化程度 (0-15)

        基于：License + Topics + Description
        """
        score = 0

        # License (0-5)
        if repo.license:
            known_licenses = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "LGPL-3.0"]
            if any(lic in repo.license for lic in known_licenses):
                score += 5
            else:
                score += 3
        # 无 License 得 0 分

        # Topics (0-5)
        topics_count = len(repo.topics)
        if topics_count >= 5:
            score += 5
        elif topics_count >= 3:
            score += 4
        elif topics_count >= 1:
            score += 3
        # 无 Topics 得 0 分

        # Description (0-5)
        if repo.description:
            desc_len = len(repo.description)
            if desc_len >= 100:
                score += 5
            elif desc_len >= 50:
                score += 4
            elif desc_len >= 20:
                score += 3
            elif desc_len > 0:
                score += 2
        # 无 Description 得 0 分

        return min(score, 15)

    def _calculate_maintenance(
        self, repo: RepositoryInfo, recent_commits: int, contributors_count: int
    ) -> int:
        """计算维护性/风险 (0-10)

        基于：维护者数量 + 维护频率
        """
        score = 10  # 基础分

        # 单一维护者风险 (-3)
        if contributors_count == 1:
            score -= 3
        elif contributors_count <= 3:
            score -= 1

        # 长期未更新风险 (-3)
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(updated.tzinfo) - updated).days
            if days_since_update > 365:
                score -= 3
            elif days_since_update > 180:
                score -= 2
            elif days_since_update > 90:
                score -= 1
        except (ValueError, TypeError):
            pass

        # Issue 积压风险 (-2)
        stars = max(repo.stars, 1)
        issue_ratio = repo.open_issues / stars
        if issue_ratio > 0.5:
            score -= 2
        elif issue_ratio > 0.2:
            score -= 1

        return max(score, 0)


health_score_service = HealthScoreService()