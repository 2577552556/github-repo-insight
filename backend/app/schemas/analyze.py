from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class ProjectType(str, Enum):
    """项目类型枚举 (9大类型)"""
    PERSONAL = "personal"              # 个人项目/工具库
    COMMUNITY = "community"           # 社区驱动的开源项目
    CORPORATE = "corporate"           # 企业主导的开源项目
    OPENCORE = "opencore"            # 核心开源 + 商业扩展
    SOURCE_AVAILABLE = "source_available"  # 源码可见但非开源协议
    AI_PLATFORM = "ai_platform"       # AI平台/应用
    INFRASTRUCTURE = "infrastructure" # 基础设施
    SDK_LIB = "sdk_library"           # SDK/工具库
    DEVELOPER_TOOL = "developer_tool"  # 开发者工具


class LicenseFamily(str, Enum):
    """许可证家族"""
    PERMISSIVE = "permissive"   # MIT, Apache-2.0, BSD
    COPYLEFT = "copyleft"       # GPL, AGPL, LGPL
    PROPRIETARY = "proprietary" # NOASSERTION, Commercial
    NONE = "none"               # 无许可证


class ProjectTypeInfo(BaseModel):
    """项目类型检测结果"""
    primary_type: ProjectType
    confidence: float = Field(ge=0.0, le=1.0)
    secondary_types: list[ProjectType] = Field(default_factory=list)
    features: dict[str, Any] = Field(
        default_factory=dict,
        description="类型检测使用的特征值"
    )
    signals: list[dict] = Field(
        default_factory=list,
        description="检测信号详情"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="元数据: data_quality, consistency, cross_validation"
    )


class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="GitHub repository URL")


class RepositoryInfo(BaseModel):
    name: str
    owner: str
    full_name: str
    description: str | None
    html_url: str
    stars: int
    forks: int
    watchers: int
    open_issues: int
    language: str | None
    created_at: str
    updated_at: str
    default_branch: str
    license: str | None = None
    topics: list[str] = Field(default_factory=list)

    def get_license_family(self) -> LicenseFamily:
        """获取许可证家族"""
        if not self.license:
            return LicenseFamily.NONE

        permissives = {"MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"}
        copylefts = {"GPL-3.0", "GPL-2.0", "LGPL-3.0", "AGPL-3.0", "MPL-2.0", "EUPL-1.2"}
        proprietary = {"NOASSERTION", "Proprietary", "Commercial", "Other"}

        lic = self.license
        if lic in permissives:
            return LicenseFamily.PERMISSIVE
        elif lic in copylefts:
            return LicenseFamily.COPYLEFT
        elif lic in proprietary:
            return LicenseFamily.PROPRIETARY
        else:
            # 未知许可证默认为PROPRIETARY
            return LicenseFamily.PROPRIETARY

    def has_ai_topics(self) -> bool:
        """检查是否包含AI相关topics"""
        ai_keywords = {
            "llm", "ai", "rag", "agent", "ml", "gpt", "chatgpt",
            "langchain", "huggingface", "embedding", "vector",
            "neural", "deep-learning", "machine-learning"
        }
        topics_lower = [t.lower() for t in self.topics]
        return any(kw in topics_lower for kw in ai_keywords)

    def has_infrastructure_topics(self) -> bool:
        """检查是否包含基础设施相关topics"""
        infra_keywords = {
            "kubernetes", "docker", "cloud", "distributed", "networking",
            "service-mesh", "container", "orchestration", "helm", "k8s"
        }
        topics_lower = [t.lower() for t in self.topics]
        return any(kw in topics_lower for kw in infra_keywords)

    def has_sdk_topics(self) -> bool:
        """检查是否包含SDK相关topics"""
        sdk_keywords = {
            "sdk", "library", "framework", "api-client", "client",
            "bindings", "module", "package"
        }
        topics_lower = [t.lower() for t in self.topics]
        return any(kw in topics_lower for kw in sdk_keywords)

    def has_devtool_topics(self) -> bool:
        """检查是否包含开发者工具相关topics"""
        devtool_keywords = {
            "cli", "developer-tools", "ide-plugin", "debugging",
            "command-line", "terminal", "tool"
        }
        topics_lower = [t.lower() for t in self.topics]
        return any(kw in topics_lower for kw in devtool_keywords)


class LanguageDistribution(BaseModel):
    languages: dict[str, float] = Field(
        ..., description="Language distribution as percentages"
    )


class RepositoryMetrics(BaseModel):
    """扩展指标（信息类，不评分）"""
    recent_commits_30d: int = 0
    recent_commits_90d: int = 0
    contributors_count: int = 0
    open_issues_count: int = 0
    closed_issues_30d: int = 0
    closed_issues_90d: int = 0  # 新增：90天关闭的issue数
    open_prs_count: int = 0
    merged_prs_30d: int = 0
    merged_prs_90d: int = 0  # 新增：90天合并的PR数
    releases_count: int = 0
    latest_release_date: str | None = None
    issue_response_time_avg: float | None = None  # 小时
    issue_response_time_median: float | None = None  # 小时 (更抗极端值)
    pr_merge_time_avg: float | None = None        # 小时
    pr_merge_time_median: float | None = None      # 小时 (更抗极端值)

    # 类型检测特征
    fork_ratio: float = 0.0  # forks / stars
    external_contributor_ratio: float = 0.0  # 外部贡献者比例 (估算)


class HealthScoreDimensions(BaseModel):
    """健康评分维度 (总分 100)"""
    popularity: int = Field(0, ge=0, le=25, description="流行度 (Stars/Forks/Watchers) - 25分")
    activity: int = Field(0, ge=0, le=25, description="活跃度 (Commit频率/更新时间) - 25分")
    community: int = Field(0, ge=0, le=15, description="社区 (Contributors/Issue处理) - 15分")
    issue_governance: int = Field(0, ge=0, le=10, description="Issue治理 (响应时间/关闭率) - 10分")
    pr_governance: int = Field(0, ge=0, le=10, description="PR治理 (合并时间/合并率) - 10分")
    engineering: int = Field(0, ge=0, le=10, description="工程化 (License/README/Topics) - 10分")
    release_maintenance: float = Field(0, ge=0, le=5, description="发布维护 (发布节奏/维护风险) - 5分")


class AIMaturity(BaseModel):
    """AI 成熟度专项评分（仅 AI Platform 项目有效）"""
    model_config = ConfigDict(protected_namespaces=())

    total_score: int = Field(0, ge=0, le=100, description="AI 成熟度总分")
    capabilities: list[dict] = Field(default_factory=list, description="AI 能力列表")
    model_support: list[str] = Field(default_factory=list, description="支持的模型")
    deployment_methods: list[str] = Field(default_factory=list, description="部署方式")


class HealthScore(BaseModel):
    score: float = Field(ge=0, le=100)
    dimensions: HealthScoreDimensions
    type_detection: ProjectTypeInfo | None = Field(
        default=None,
        description="项目类型检测结果"
    )
    ai_maturity: AIMaturity | None = Field(
        default=None,
        description="AI 成熟度评分（仅 AI Platform 项目）"
    )


class AIScore(BaseModel):
    """AI 评分 (规则引擎计算，DeepSeek AI 只负责解读)"""
    score: float = Field(ge=0, le=100)
    grade: str = Field(pattern=r"^[A-F]$")
    summary: str
    ai_used: bool = Field(True, description="是否使用了 AI 解读")


class ConclusionItem(BaseModel):
    """带溯源的结论项"""
    text: str = Field(description="结论文本")
    source: str = Field(description="数据来源")
    confidence: str = Field(description="置信度: high/medium/low")
    causation: str = Field(description="因果关系: causation/correlation/unknown")


class AIAnalysis(BaseModel):
    """AI 深度解读 (DeepSeek 生成，基于规则引擎的评分结果)"""
    summary: str = Field(description="项目一句话总结")
    strengths: list[ConclusionItem] = Field(default_factory=list, description="优势分析")
    risks: list[ConclusionItem] = Field(default_factory=list, description="风险分析")
    suggestions: list[ConclusionItem] = Field(default_factory=list, description="改进建议")
    ai_used: bool = Field(True, description="是否使用了 AI 解读")


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(ser_json_timedelta="iso8601")

    repository: RepositoryInfo
    languages: LanguageDistribution
    metrics: RepositoryMetrics
    health_score: HealthScore
    ai_score: AIScore
    ai_analysis: AIAnalysis | None = Field(None, description="AI 深度解读")


class AnalysisRecordSummary(BaseModel):
    """分析记录摘要（用于列表展示）"""
    id: str
    repository_url: str
    repository_name: str
    owner: str
    full_name: str
    score: float | None = None
    grade: str | None = None
    type_detection: dict | None = None
    status: str = Field(description="processing/completed/failed")
    error_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AnalysisRecord(AnalysisRecordSummary):
    """分析记录完整信息（包含结果）"""
    result_json: AnalyzeResponse | None = None