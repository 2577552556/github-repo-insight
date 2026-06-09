from pydantic import BaseModel, Field, ConfigDict


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
    open_prs_count: int = 0
    merged_prs_30d: int = 0
    releases_count: int = 0
    latest_release_date: str | None = None
    issue_response_time_avg: float | None = None  # 小时
    pr_merge_time_avg: float | None = None        # 小时


class HealthScoreDimensions(BaseModel):
    """健康评分维度 (总分 100)"""
    popularity: int = Field(0, ge=0, le=25, description="流行度 (Stars/Forks/Watchers) - 25分")
    activity: int = Field(0, ge=0, le=25, description="活跃度 (Commit频率/更新时间) - 25分")
    community: int = Field(0, ge=0, le=15, description="社区 (Contributors/Issue处理) - 15分")
    issue_governance: int = Field(0, ge=0, le=10, description="Issue治理 (响应时间/关闭率) - 10分")
    pr_governance: int = Field(0, ge=0, le=10, description="PR治理 (合并时间/合并率) - 10分")
    engineering: int = Field(0, ge=0, le=10, description="工程化 (License/README/Topics) - 10分")
    release_maintenance: int = Field(0, ge=0, le=5, description="发布维护 (发布节奏/维护风险) - 5分")


class HealthScore(BaseModel):
    score: int = Field(ge=0, le=100)
    dimensions: HealthScoreDimensions


class AIScore(BaseModel):
    """AI 评分 (规则引擎计算，DeepSeek AI 只负责解读)"""
    score: int = Field(ge=0, le=100)
    grade: str = Field(pattern=r"^[A-F]$")
    summary: str
    ai_used: bool = Field(True, description="是否使用了 AI 解读")


class AIAnalysis(BaseModel):
    """AI 深度解读 (DeepSeek 生成，基于规则引擎的评分结果)"""
    summary: str = Field(description="项目一句话总结")
    strengths: list[str] = Field(default_factory=list, description="优势分析")
    risks: list[str] = Field(default_factory=list, description="风险分析")
    suggestions: list[str] = Field(default_factory=list, description="改进建议")
    ai_used: bool = Field(True, description="是否使用了 AI 解读")


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(ser_json_timedelta="iso8601")

    repository: RepositoryInfo
    languages: LanguageDistribution
    metrics: RepositoryMetrics
    health_score: HealthScore
    ai_score: AIScore
    ai_analysis: AIAnalysis | None = Field(None, description="AI 深度解读")