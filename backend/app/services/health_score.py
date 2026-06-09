from datetime import datetime, timezone
from enum import Enum

from app.schemas.analyze import (
    RepositoryInfo,
    RepositoryMetrics,
    HealthScore,
    HealthScoreDimensions,
)


class ProjectType(str, Enum):
    """项目类型枚举"""
    PERSONAL = "personal"           # 个人项目/工具库
    COMMUNITY = "community"          # 社区驱动的开源项目
    CORPORATE = "corporate"         # 企业主导的开源项目
    OPENCORE = "opencore"           # 核心开源 + 商业扩展


# 商业License列表
COMMERCIAL_LICENSES = {"NOASSERTION", "Proprietary", "Commercial"}


def detect_project_type(repo: RepositoryInfo) -> tuple[ProjectType, float]:
    """检测项目类型及置信度

    决策树：
    1. stars > 10000?
       Y → forks/stars > 0.3? → Corporate
           forks/stars <= 0.3? → license in COMMERCIAL? → OpenCore : Community
       N → description包含工具类关键词? → Personal : Community
    """
    stars = repo.stars
    forks = repo.forks
    license_info = repo.license
    description = (repo.description or "").lower()

    # 工具类关键词
    tool_keywords = {"tool", "library", "framework", "sdk", "cli", "utility", "module", "package", "plugin", "extension"}

    # Q1: 高星项目检测
    if stars > 10000:
        # Q2: fork比率
        fork_ratio = forks / stars if stars > 0 else 0
        if fork_ratio > 0.3:
            return ProjectType.CORPORATE, 0.9
        # Q3: license检测
        if license_info in COMMERCIAL_LICENSES:
            return ProjectType.OPENCORE, 0.8
        return ProjectType.COMMUNITY, 0.7

    # Q4: 低星项目检测
    if any(kw in description for kw in tool_keywords):
        return ProjectType.PERSONAL, 0.6

    return ProjectType.COMMUNITY, 0.5


# 类型自适应基准线
# 不同类型项目有不同的Issue响应时间期望
TYPE_BASELINES = {
    ProjectType.PERSONAL: {
        "issue_response_hours": 168,   # 7天
        "pr_merge_hours": 336,          # 14天
        "min_commits_30d": 2,          # 最低期望commits
    },
    ProjectType.COMMUNITY: {
        "issue_response_hours": 72,    # 3天
        "pr_merge_hours": 168,          # 7天
        "min_commits_30d": 5,
    },
    ProjectType.CORPORATE: {
        "issue_response_hours": 24,    # 1天
        "pr_merge_hours": 72,           # 3天
        "min_commits_30d": 10,
    },
    ProjectType.OPENCORE: {
        "issue_response_hours": 72,    # 3天
        "pr_merge_hours": 168,          # 7天
        "min_commits_30d": 5,
    },
}


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
        """计算健康评分（基于7个维度，自动适配项目类型）"""
        # 首先检测项目类型
        project_type, type_confidence = detect_project_type(repository)
        baseline = TYPE_BASELINES[project_type]

        popularity = self._calculate_popularity(repository)
        activity = self._calculate_activity(repository, metrics, baseline)
        community = self._calculate_community(repository, metrics)
        issue_governance = self._calculate_issue_governance(repository, metrics, baseline)
        pr_governance = self._calculate_pr_governance(repository, metrics, baseline)
        engineering = self._calculate_engineering(repository, project_type)
        release_maintenance = self._calculate_release_maintenance(repository, metrics, project_type)

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

    def _calculate_activity(self, repo: RepositoryInfo, metrics: RepositoryMetrics, baseline: dict) -> int:
        """计算活跃度 (0-25分)

        基于：更新时间 + 近期 Commit 数量（使用类型基准线）
        """
        score = 0
        min_commits = baseline.get("min_commits_30d", 5)

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

        # Commit 频率评分 (0-15)，使用类型基准线调整
        commits_30d = metrics.recent_commits_30d
        commits_90d = metrics.recent_commits_90d

        # 基准线调整：个人项目期望低，企业项目期望高
        if commits_30d >= min_commits * 20:  # 远超期望
            score += 15
        elif commits_30d >= min_commits * 10:
            score += 12
        elif commits_30d >= min_commits * 4:
            score += 9
        elif commits_30d >= min_commits * 2:
            score += 6
        elif commits_30d >= min_commits:
            score += 3
        elif commits_30d > 0:
            score += 1
        # 0 commits 得 0 分

        # 90天趋势加分 (0-5)
        trend_factor = min_commits * 30  # 基准线的30倍
        if commits_90d >= trend_factor * 2:
            score += 5
        elif commits_90d >= trend_factor:
            score += 4
        elif commits_90d >= trend_factor * 0.5:
            score += 3
        elif commits_90d >= trend_factor * 0.2:
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
        # 使用近30天关闭率，而非 open/stars 比率
        # stars 多不代表 issue 处理得好，应该看实际关闭了多少
        closed_30d = metrics.closed_issues_30d
        open_issues_count = metrics.open_issues_count
        total_issues = closed_30d + open_issues_count

        if total_issues > 0:
            close_rate = closed_30d / total_issues
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
        # 无issue数据时不加分也不减分

        return min(score, 15)

    def _calculate_issue_governance(
        self, repo: RepositoryInfo, metrics: RepositoryMetrics, baseline: dict
    ) -> int:
        """计算 Issue 治理能力 (0-10分)

        基于：Issue 响应时间（类型自适应）+ 30天关闭率
        """
        score = 0
        response_baseline = baseline.get("issue_response_hours", 72)

        # 响应时间评分 (0-5)，使用类型基准线
        avg_response_time = metrics.issue_response_time_avg
        if avg_response_time is not None:
            # 类型自适应：Personal项目基准宽松，Corporate项目基准严格
            if avg_response_time <= response_baseline * 0.5:
                score += 5
            elif avg_response_time <= response_baseline:
                score += 4
            elif avg_response_time <= response_baseline * 2:
                score += 3
            elif avg_response_time <= response_baseline * 4:
                score += 2
            elif avg_response_time <= response_baseline * 8:
                score += 1
            # 超过基准线8倍得 0 分
        else:
            # 无数据时根据 open issues 数量估算
            if metrics.open_issues_count <= 5:
                score += 3
            elif metrics.open_issues_count <= 20:
                score += 2
            elif metrics.open_issues_count <= 50:
                score += 1

        # 30天关闭率评分 (0-5)
        closed_30d = metrics.closed_issues_30d
        open_issues = metrics.open_issues_count

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

        return min(score, 10)

    def _calculate_pr_governance(self, repo: RepositoryInfo, metrics: RepositoryMetrics, baseline: dict) -> int:
        """计算 PR 治理能力 (0-10分)

        基于：PR 合并时间（类型自适应）+ 30天合并率
        """
        score = 0
        merge_baseline = baseline.get("pr_merge_hours", 168)

        # 合并时间评分 (0-5)，使用类型基准线
        avg_merge_time = metrics.pr_merge_time_avg
        if avg_merge_time is not None:
            if avg_merge_time <= merge_baseline * 0.5:
                score += 5
            elif avg_merge_time <= merge_baseline:
                score += 4
            elif avg_merge_time <= merge_baseline * 2:
                score += 3
            elif avg_merge_time <= merge_baseline * 4:
                score += 2
            elif avg_merge_time <= merge_baseline * 8:
                score += 1
            # 超过基准线8倍得 0 分
        else:
            # 无数据时根据 open PRs 数量估算
            # Open Core 项目可能PR少，因为核心开发走内部
            if metrics.open_prs_count <= 5:
                score += 3
            elif metrics.open_prs_count <= 20:
                score += 2
            elif metrics.open_prs_count <= 50:
                score += 1

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

    def _calculate_engineering(self, repo: RepositoryInfo, project_type: ProjectType) -> int:
        """计算工程化程度 (0-10分)

        基于：License + Topics + Description
        License评分按项目类型调整：Corporate/OpenCore 对 License 要求较低
        """
        score = 0

        # License (0-4)
        # Corporate 和 OpenCore 项目可能使用 proprietary license，这是设计选择
        if repo.license:
            known_licenses = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "LGPL-3.0"]
            if any(lic in repo.license for lic in known_licenses):
                score += 4
            elif repo.license in COMMERCIAL_LICENSES:
                # 商业License对Corporate/OpenCore是正常的
                if project_type in (ProjectType.CORPORATE, ProjectType.OPENCORE):
                    score += 3
                else:
                    score += 1
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

        # Description (0-3)
        if repo.description:
            desc_len = len(repo.description)
            if desc_len >= 100:
                score += 3
            elif desc_len >= 50:
                score += 2
            elif desc_len >= 20:
                score += 1

        return min(score, 10)

    def _calculate_release_maintenance(
        self, repo: RepositoryInfo, metrics: RepositoryMetrics, project_type: ProjectType
    ) -> int:
        """计算发布维护能力 (0-5分)

        基于：发布频率 + 维护风险（按项目类型调整）
        """
        score = 0

        # 发布频率评分 (0-3)
        releases_count = metrics.releases_count
        latest_release = metrics.latest_release_date

        if releases_count == 0:
            # Personal 项目可能不做 releases
            if project_type == ProjectType.PERSONAL:
                score += 1
            else:
                score += 0
        elif releases_count >= 50:
            score += 3
        elif releases_count >= 20:
            score += 2
        elif releases_count >= 5:
            score += 1
        else:
            score += 1

        # 最近更新时间风险（按项目类型调整）
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(timezone.utc) - updated).days

            # Corporate 项目更新应该更频繁
            if project_type == ProjectType.CORPORATE:
                if days_since_update > 365:
                    score -= 2
                elif days_since_update > 180:
                    score -= 1
                elif days_since_update > 90:
                    score -= 0.5
            elif project_type == ProjectType.COMMUNITY:
                if days_since_update > 730:
                    score -= 2
                elif days_since_update > 365:
                    score -= 1
                elif days_since_update > 180:
                    score -= 0.5
            else:  # Personal, OpenCore
                if days_since_update > 730:
                    score -= 1
                elif days_since_update > 365:
                    score -= 0.5
        except (ValueError, TypeError):
            pass

        # 单一维护者风险（Personal 项目预期是单人开发）
        if project_type != ProjectType.PERSONAL:
            if metrics.contributors_count == 1:
                score -= 1
            elif metrics.contributors_count <= 3:
                score -= 0.5

        return max(0, min(score, 5))


health_score_service = HealthScoreService()