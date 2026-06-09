from datetime import datetime, timezone
from app.schemas.analyze import (
    RepositoryInfo,
    RepositoryMetrics,
    HealthScore,
    HealthScoreDimensions,
    ProjectType,
    ProjectTypeInfo,
    LicenseFamily,
)


# 商业License列表
COMMERCIAL_LICENSES = {"NOASSERTION", "Proprietary", "Commercial"}

# 扩展的License白名单（更全面）
KNOWN_LICENSES = {
    # Permissive (得满分)
    "MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense",
    "PostgreSQL", "BlueOak-1.0.0", "CC0-1.0", "0BSD", "BSD-3-Clause-Clear",
    # Copyleft (得满分)
    "GPL-3.0", "GPL-2.0", "LGPL-3.0", "LGPL-2.1", "AGPL-3.0", "MPL-2.0", "EUPL-1.2",
    # 其他开源License
    "CC-BY-4.0", "CC-BY-SA-4.0", "WTFPL", "BSL-1.0",
}


def detect_project_type(
    repo: RepositoryInfo,
    metrics: RepositoryMetrics | None = None
) -> ProjectTypeInfo:
    """检测项目类型及置信度 (9大类型)

    决策树：
    1. AI Platform 检测 (最高优先级)
    2. Infrastructure 检测
    3. SDK/Library 检测
    4. Developer Tool 检测
    5. Source Available 检测
    6. Open Core 检测
    7. Corporate 检测
    8. Community 检测
    9. Personal 检测

    返回 ProjectTypeInfo 包含：
    - primary_type: 主要类型
    - confidence: 置信度
    - secondary_types: 次要类型
    - features: 使用的特征
    - signals: 检测信号
    - metadata: 元数据
    """
    signals = []
    features = {}

    # ========== 特征提取 ==========

    # 基础特征
    stars = repo.stars
    forks = repo.forks
    fork_ratio = forks / stars if stars > 0 else 0.0
    features["fork_ratio"] = fork_ratio
    features["stars"] = stars

    # License 家族
    license_family = repo.get_license_family()
    features["license_family"] = license_family.value
    is_commercial_license = license_family == LicenseFamily.PROPRIETARY

    # Topic 特征
    has_ai = repo.has_ai_topics()
    has_infra = repo.has_infrastructure_topics()
    has_sdk = repo.has_sdk_topics()
    has_devtool = repo.has_devtool_topics()

    features["has_ai_topics"] = float(has_ai)
    features["has_infrastructure_topics"] = float(has_infra)
    features["has_sdk_topics"] = float(has_sdk)
    features["has_devtool_topics"] = float(has_devtool)

    # 外部贡献者比例 (如果有metrics)
    if metrics and metrics.external_contributor_ratio > 0:
        ext_ratio = metrics.external_contributor_ratio
    else:
        # 估算：基于stars规模
        if stars > 10000:
            ext_ratio = 0.3  # 大型项目外部贡献通常较低
        elif stars > 1000:
            ext_ratio = 0.5
        else:
            ext_ratio = 0.6

    features["external_contributor_ratio"] = ext_ratio

    # ========== 类型检测决策树 ==========

    type_scores: dict[ProjectType, tuple[float, str]] = {}

    # ---------- 1. AI Platform 检测 ----------
    if has_ai:
        ai_signals = []
        if has_ai:
            ai_signals.append("topics含AI相关关键词")
        if "rag" in [t.lower() for t in repo.topics]:
            ai_signals.append("支持RAG")
        if "agent" in [t.lower() for t in repo.topics]:
            ai_signals.append("支持Agent")
        if "workflow" in [t.lower() for t in repo.topics]:
            ai_signals.append("支持工作流")

        confidence = 0.75 + 0.05 * len(ai_signals)
        type_scores[ProjectType.AI_PLATFORM] = (
            min(confidence, 0.95),
            f"AI关键词检测: {', '.join(ai_signals)}"
        )

    # ---------- 2. Infrastructure 检测 ----------
    if has_infra or fork_ratio > 0.25:
        infra_signals = []
        if has_infra:
            infra_signals.append("topics含infrastructure关键词")
        if fork_ratio > 0.25:
            infra_signals.append(f"fork比率较高({fork_ratio:.2f})")

        confidence = 0.70 + 0.05 * len(infra_signals)
        type_scores[ProjectType.INFRASTRUCTURE] = (
            min(confidence, 0.90),
            f"Infrastructure检测: {', '.join(infra_signals)}"
        )

    # ---------- 3. SDK/Library 检测 ----------
    if has_sdk or (stars > 1000 and not has_ai and not has_infra):
        sdk_signals = []
        if has_sdk:
            sdk_signals.append("topics含SDK/Library关键词")
        if stars > 1000:
            sdk_signals.append("中等stars规模(适合SDK)")

        confidence = 0.65 + 0.05 * len(sdk_signals)
        type_scores[ProjectType.SDK_LIB] = (
            min(confidence, 0.85),
            f"SDK/Library检测: {', '.join(sdk_signals)}"
        )

    # ---------- 4. Developer Tool 检测 ----------
    if has_devtool:
        type_scores[ProjectType.DEVELOPER_TOOL] = (
            0.70,
            "topics含开发者工具关键词"
        )

    # ---------- 5. Source Available 检测 ----------
    if is_commercial_license and license_family != LicenseFamily.NONE:
        # 商业License但不是完全Proprietary
        if "source" in (repo.description or "").lower() or "available" in (repo.description or "").lower():
            type_scores[ProjectType.SOURCE_AVAILABLE] = (
                0.75,
                "商业License且描述暗示源码可见"
            )

    # ---------- 6. Open Core 检测 ----------
    if is_commercial_license:
        opencore_signals = []
        if is_commercial_license:
            opencore_signals.append("商业License(NOASSERTION/Proprietary)")
        if "enterprise" in (repo.description or "").lower():
            opencore_signals.append("描述提及企业版")
        if "open" in (repo.description or "").lower() and "core" in (repo.description or "").lower():
            opencore_signals.append("描述提及Open Core")

        if opencore_signals:
            confidence = 0.65 + 0.05 * len(opencore_signals)
            type_scores[ProjectType.OPENCORE] = (
                min(confidence, 0.85),
                f"OpenCore检测: {', '.join(opencore_signals)}"
            )

    # ---------- 7. Corporate 检测 ----------
    if stars > 10000 and fork_ratio > 0.2:
        corporate_signals = []
        if stars > 10000:
            corporate_signals.append(f"高stars({stars})")
        if fork_ratio > 0.2:
            corporate_signals.append(f"高fork比率({fork_ratio:.2f})")
        if is_commercial_license:
            corporate_signals.append("商业License")

        confidence = 0.70 + 0.05 * len(corporate_signals)
        type_scores[ProjectType.CORPORATE] = (
            min(confidence, 0.90),
            f"Corporate检测: {', '.join(corporate_signals)}"
        )

    # ---------- 8. Community 检测 ----------
    if stars > 5000 and ext_ratio > 0.4:
        community_signals = []
        if stars > 5000:
            community_signals.append(f"中高stars({stars})")
        if ext_ratio > 0.4:
            community_signals.append(f"外部贡献比例高({ext_ratio:.2f})")

        confidence = 0.60 + 0.05 * len(community_signals)
        type_scores[ProjectType.COMMUNITY] = (
            min(confidence, 0.85),
            f"Community检测: {', '.join(community_signals)}"
        )

    # ---------- 9. Personal 检测 ----------
    if stars < 5000 and not has_ai and not has_infra and not has_sdk and not has_devtool:
        personal_signals = []
        if stars < 5000:
            personal_signals.append(f"低stars({stars})")
        if not has_ai and not has_infra:
            personal_signals.append("非AI/Infra领域")

        confidence = 0.55 + 0.05 * len(personal_signals)
        type_scores[ProjectType.PERSONAL] = (
            min(confidence, 0.75),
            f"Personal检测: {', '.join(personal_signals)}"
        )

    # ========== 确定主类型 ==========

    if not type_scores:
        # 默认Community
        primary_type = ProjectType.COMMUNITY
        primary_confidence = 0.50
        primary_reason = "默认类型"
    else:
        # 按置信度排序
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1][0], reverse=True)
        primary_type, (primary_confidence, primary_reason) = sorted_types[0]

    # 构建信号列表
    signals = [
        {"type": "keyword", "name": primary_reason, "weight": primary_confidence}
    ]

    # 次要类型
    secondary_types = [
        pt for pt, _ in sorted_types[1:4] if pt != primary_type
    ][:3]

    # ========== 计算元数据 ==========

    # 数据质量分数
    data_quality = 0.5
    if repo.license:
        data_quality += 0.1
    if repo.topics:
        data_quality += 0.1
    if repo.description:
        data_quality += 0.1
    if stars > 100:
        data_quality += 0.1
    if metrics and metrics.contributors_count > 5:
        data_quality += 0.1

    # 一致性分数 (类型信号之间的一致性)
    consistency = 0.8 if len(type_scores) > 2 else 0.9

    # 交叉验证分数
    cross_validation = 0.85

    metadata = {
        "data_quality_score": min(data_quality, 1.0),
        "consistency_score": consistency,
        "cross_validation_score": cross_validation,
    }

    return ProjectTypeInfo(
        primary_type=primary_type,
        confidence=primary_confidence,
        secondary_types=secondary_types,
        features=features,
        signals=signals,
        metadata=metadata,
    )


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
    ProjectType.SOURCE_AVAILABLE: {
        "issue_response_hours": 120,   # 5天
        "pr_merge_hours": 240,         # 10天
        "min_commits_30d": 3,
    },
    ProjectType.AI_PLATFORM: {
        "issue_response_hours": 96,    # 4天
        "pr_merge_hours": 168,          # 7天
        "min_commits_30d": 8,
    },
    ProjectType.INFRASTRUCTURE: {
        "issue_response_hours": 48,    # 2天
        "pr_merge_hours": 96,           # 4天
        "min_commits_30d": 15,
    },
    ProjectType.SDK_LIB: {
        "issue_response_hours": 120,   # 5天
        "pr_merge_hours": 168,          # 7天
        "min_commits_30d": 5,
    },
    ProjectType.DEVELOPER_TOOL: {
        "issue_response_hours": 96,    # 4天
        "pr_merge_hours": 120,           # 5天
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
        # 检测项目类型
        type_detection = detect_project_type(repository, metrics)
        project_type = type_detection.primary_type
        baseline = TYPE_BASELINES.get(project_type, TYPE_BASELINES[ProjectType.COMMUNITY])

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
            type_detection=type_detection,
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

        基于：更新时间 + 近期 Commit 数量（使用类型基准线 + 规模归一化）
        规模归一化：normalized = raw / sqrt(contributors)，避免大项目刷分
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

        # Commit 频率评分 (0-15)，使用类型基准线 + 规模归一化
        commits_30d = metrics.recent_commits_30d
        commits_90d = metrics.recent_commits_90d

        # 规模归一化：使用 sqrt(contributors) 作为规模因子
        # 10人项目的100 commits 变成 100/sqrt(10) ≈ 31.6
        # 1人项目的100 commits 保持 100
        scale_factor = max(metrics.contributors_count, 1) ** 0.5
        normalized_commits_30d = commits_30d / scale_factor
        normalized_commits_90d = commits_90d / scale_factor

        # 基准线调整：个人项目期望低，企业项目期望高
        if normalized_commits_30d >= min_commits * 20:  # 远超期望
            score += 15
        elif normalized_commits_30d >= min_commits * 10:
            score += 12
        elif normalized_commits_30d >= min_commits * 4:
            score += 9
        elif normalized_commits_30d >= min_commits * 2:
            score += 6
        elif normalized_commits_30d >= min_commits:
            score += 3
        elif normalized_commits_30d > 0:
            score += 1
        # 0 commits 得 0 分

        # 90天趋势加分 (0-5)
        trend_factor = min_commits * 30  # 基准线的30倍
        if normalized_commits_90d >= trend_factor * 2:
            score += 5
        elif normalized_commits_90d >= trend_factor:
            score += 4
        elif normalized_commits_90d >= trend_factor * 0.5:
            score += 3
        elif normalized_commits_90d >= trend_factor * 0.2:
            score += 2
        elif normalized_commits_90d > 0:
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

        基于：Issue 响应时间（中位数优先，更抗极端值）+ 30天关闭率
        """
        score = 0
        response_baseline = baseline.get("issue_response_hours", 72)

        # 优先使用中位数，其次平均值（更抗极端值）
        response_time = metrics.issue_response_time_median or metrics.issue_response_time_avg
        if response_time is not None:
            # 类型自适应：Personal项目基准宽松，Corporate项目基准严格
            if response_time <= response_baseline * 0.5:
                score += 5
            elif response_time <= response_baseline:
                score += 4
            elif response_time <= response_baseline * 2:
                score += 3
            elif response_time <= response_baseline * 4:
                score += 2
            elif response_time <= response_baseline * 8:
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

        基于：PR 合并时间（中位数优先）+ 30天合并率
        """
        score = 0
        merge_baseline = baseline.get("pr_merge_hours", 168)

        # 优先使用中位数，其次平均值（更抗极端值）
        merge_time = metrics.pr_merge_time_median or metrics.pr_merge_time_avg
        if merge_time is not None:
            if merge_time <= merge_baseline * 0.5:
                score += 5
            elif merge_time <= merge_baseline:
                score += 4
            elif merge_time <= merge_baseline * 2:
                score += 3
            elif merge_time <= merge_baseline * 4:
                score += 2
            elif merge_time <= merge_baseline * 8:
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
            # 使用扩展的白名单
            if any(lic in repo.license for lic in KNOWN_LICENSES):
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