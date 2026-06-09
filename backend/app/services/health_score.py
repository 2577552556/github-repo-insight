from datetime import datetime, timezone

from app.schemas.analyze import (
    RepositoryInfo,
    RepositoryMetrics,
    HealthScore,
    HealthScoreDimensions,
)


def calculate_grade(score: int) -> str:
    """根据分数计算等级: A≥90, B≥80, C≥70, D≥60, E≥50, F<50"""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    if score >= 50:
        return "E"
    return "F"


class HealthScoreService:
    """仓库健康评分服务（规则引擎，100分制）

    评分维度：
    - Popularity (25分): Stars/Forks/Watchers
    - Activity (25分): Commit频率/更新时间
    - Community (15分): Contributors/Issue处理
    - Issue Governance (10分): Issue响应/关闭率
    - PR Governance (10分): PR合并时间/合并率
    - Engineering (10分): License/README/Topics
    - Release/Maintenance (5分): 发布节奏/维护风险
    """

    def calculate(
        self,
        repository: RepositoryInfo,
        metrics: RepositoryMetrics,
    ) -> HealthScore:
        """计算健康评分（基于7个维度）"""
        popularity = self._calculate_popularity(repository)
        activity = self._calculate_activity(repository, metrics)
        community = self._calculate_community(repository, metrics)
        issue_governance = self._calculate_issue_governance(repository, metrics)
        pr_governance = self._calculate_pr_governance(repository, metrics)
        engineering = self._calculate_engineering(repository)
        release_maintenance = self._calculate_release_maintenance(repository, metrics)

        total_score = (
            popularity
            + activity
            + community
            + issue_governance
            + pr_governance
            + engineering
            + release_maintenance
        )

        return HealthScore(
            score=total_score,
            dimensions=HealthScoreDimensions(
                popularity=popularity,
                activity=activity,
                community=community,
                issue_governance=issue_governance,
                pr_governance=pr_governance,
                engineering=engineering,
                release_maintenance=release_maintenance,
            ),
        )

    def _calculate_popularity(self, repo: RepositoryInfo) -> int:
        """计算流行度 (0-25分)

        Stars: <100=1, <1k=5, <10k=10, <50k=15, <100k=20, >=100k=25
        Forks: 额外加分 (反映实际使用)
        Watchers: 额外加分
        """
        score = 0

        # Stars 评分 (0-15)
        stars = repo.stars
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

        # Forks 加分 (0-5)
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

        # Watchers 加分 (0-5)
        watchers = repo.watchers
        if watchers >= 5000:
            score += 5
        elif watchers >= 1000:
            score += 3
        elif watchers >= 100:
            score += 1

        return min(score, 25)

    def _calculate_activity(self, repo: RepositoryInfo, metrics: RepositoryMetrics) -> int:
        """计算活跃度 (0-25分)

        基于：更新时间 + 近期 Commit 数量
        """
        score = 0

        # 更新时间评分 (0-10)
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(timezone.utc) - updated).days

            if days_since_update <= 7:
                score += 10
            elif days_since_update <= 30:
                score += 8
            elif days_since_update <= 90:
                score += 5
            elif days_since_update <= 180:
                score += 3
            elif days_since_update <= 365:
                score += 1
        except (ValueError, TypeError):
            score += 3  # 默认中等

        # Commit 频率评分 (0-15)
        commits_30d = metrics.recent_commits_30d
        commits_90d = metrics.recent_commits_90d

        if commits_30d >= 100:
            score += 15
        elif commits_30d >= 50:
            score += 12
        elif commits_30d >= 20:
            score += 9
        elif commits_30d >= 10:
            score += 6
        elif commits_30d >= 5:
            score += 3
        elif commits_30d > 0:
            score += 1
        # 0 commits 得 0 分

        # 90天趋势加分 (0-5)
        if commits_90d >= 300:
            score += 5
        elif commits_90d >= 150:
            score += 4
        elif commits_90d >= 50:
            score += 3
        elif commits_90d >= 20:
            score += 2
        elif commits_90d > 0:
            score += 1

        return min(score, 25)

    def _calculate_community(self, repo: RepositoryInfo, metrics: RepositoryMetrics) -> int:
        """计算社区活跃度 (0-15分)

        基于：Contributors 数量 + Issue 处理情况
        """
        score = 0

        # Contributors 评分 (0-10)
        contributors = metrics.contributors_count
        if contributors >= 100:
            score += 10
        elif contributors >= 50:
            score += 8
        elif contributors >= 20:
            score += 6
        elif contributors >= 10:
            score += 4
        elif contributors >= 5:
            score += 2
        elif contributors >= 2:
            score += 1
        # 只有 1 个贡献者得 0 分

        # Issue 处理率评分 (0-5)
        stars = max(repo.stars, 1)
        open_issues = repo.open_issues
        issue_ratio = open_issues / stars

        if issue_ratio <= 0.01:
            score += 5
        elif issue_ratio <= 0.05:
            score += 4
        elif issue_ratio <= 0.1:
            score += 3
        elif issue_ratio <= 0.2:
            score += 2
        elif issue_ratio <= 0.5:
            score += 1
        # issue 过多得 0 分

        return min(score, 15)

    def _calculate_issue_governance(
        self, repo: RepositoryInfo, metrics: RepositoryMetrics
    ) -> int:
        """计算 Issue 治理能力 (0-10分)

        基于：Issue 响应时间 + 30天关闭率
        """
        score = 0

        # 响应时间评分 (0-5)
        avg_response_time = metrics.issue_response_time_avg
        if avg_response_time is not None:
            if avg_response_time <= 24:  # 24小时内
                score += 5
            elif avg_response_time <= 72:  # 3天内
                score += 4
            elif avg_response_time <= 168:  # 7天内
                score += 3
            elif avg_response_time <= 336:  # 14天内
                score += 2
            elif avg_response_time <= 720:  # 30天内
                score += 1
            # 超过30天得 0 分
        else:
            # 无数据时根据 open issues 数量估算
            if repo.open_issues <= 5:
                score += 3
            elif repo.open_issues <= 20:
                score += 2
            elif repo.open_issues <= 50:
                score += 1
            # 超过50个 open issues 得 0 分

        # 30天关闭率评分 (0-5)
        closed_30d = metrics.closed_issues_30d
        open_issues = repo.open_issues

        if closed_30d > 0:
            total_possible = closed_30d + open_issues
            close_rate = closed_30d / total_possible if total_possible > 0 else 0

            if close_rate >= 0.8:
                score += 5
            elif close_rate >= 0.6:
                score += 4
            elif close_rate >= 0.4:
                score += 3
            elif close_rate >= 0.2:
                score += 2
            elif close_rate > 0:
                score += 1
            # close_rate == 0 得 0 分

        return min(score, 10)

    def _calculate_pr_governance(self, repo: RepositoryInfo, metrics: RepositoryMetrics) -> int:
        """计算 PR 治理能力 (0-10分)

        基于：PR 合并时间 + 30天合并率
        """
        score = 0

        # 合并时间评分 (0-5)
        avg_merge_time = metrics.pr_merge_time_avg
        if avg_merge_time is not None:
            if avg_merge_time <= 24:  # 24小时内
                score += 5
            elif avg_merge_time <= 72:  # 3天内
                score += 4
            elif avg_merge_time <= 168:  # 7天内
                score += 3
            elif avg_merge_time <= 336:  # 14天内
                score += 2
            elif avg_merge_time <= 720:  # 30天内
                score += 1
            # 超过30天得 0 分
        else:
            # 无数据时根据 open PRs 数量估算
            if metrics.open_prs_count <= 5:
                score += 3
            elif metrics.open_prs_count <= 20:
                score += 2
            elif metrics.open_prs_count <= 50:
                score += 1
            # 超过50个 open PRs 得 0 分

        # 30天合并率评分 (0-5)
        merged_30d = metrics.merged_prs_30d
        open_prs = metrics.open_prs_count

        if merged_30d > 0:
            total_possible = merged_30d + open_prs
            merge_rate = merged_30d / total_possible if total_possible > 0 else 0

            if merge_rate >= 0.8:
                score += 5
            elif merge_rate >= 0.6:
                score += 4
            elif merge_rate >= 0.4:
                score += 3
            elif merge_rate >= 0.2:
                score += 2
            elif merge_rate > 0:
                score += 1
            # merge_rate == 0 得 0 分

        return min(score, 10)

    def _calculate_engineering(self, repo: RepositoryInfo) -> int:
        """计算工程化程度 (0-10分)

        基于：License + Topics + Description
        """
        score = 0

        # License (0-4)
        if repo.license:
            known_licenses = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "LGPL-3.0"]
            if any(lic in repo.license for lic in known_licenses):
                score += 4
            else:
                score += 2
        # 无 License 得 0 分

        # Topics (0-3)
        topics_count = len(repo.topics)
        if topics_count >= 5:
            score += 3
        elif topics_count >= 3:
            score += 2
        elif topics_count >= 1:
            score += 1
        # 无 Topics 得 0 分

        # Description (0-3)
        if repo.description:
            desc_len = len(repo.description)
            if desc_len >= 100:
                score += 3
            elif desc_len >= 50:
                score += 2
            elif desc_len >= 20:
                score += 1
        # 无 Description 得 0 分

        return min(score, 10)

    def _calculate_release_maintenance(
        self, repo: RepositoryInfo, metrics: RepositoryMetrics
    ) -> int:
        """计算发布维护能力 (0-5分)

        基于：发布频率 + 维护风险
        """
        score = 0

        # 发布频率评分 (0-3)
        releases_count = metrics.releases_count
        latest_release = metrics.latest_release_date

        if releases_count == 0:
            score += 0  # 从未发布
        elif releases_count >= 50:
            score += 3
        elif releases_count >= 20:
            score += 2
        elif releases_count >= 5:
            score += 1
        else:
            score += 1  # 至少有1个发布

        # 最近更新时间风险 (-2)
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(timezone.utc) - updated).days

            if days_since_update > 730:  # 2年未更新
                score -= 2
            elif days_since_update > 365:  # 1年未更新
                score -= 1
            elif days_since_update > 180:  # 半年未更新
                score -= 0.5
        except (ValueError, TypeError):
            pass

        # 单一维护者风险 (-1)
        if metrics.contributors_count == 1:
            score -= 1
        elif metrics.contributors_count <= 3:
            score -= 0.5

        return max(0, min(score, 5))


health_score_service = HealthScoreService()