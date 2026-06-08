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
    license: str | None = None  # 新增：开源协议
    topics: list[str] = Field(default_factory=list)  # 新增：主题标签


class LanguageDistribution(BaseModel):
    languages: dict[str, float] = Field(
        ..., description="Language distribution as percentages"
    )


class HealthScoreDimensions(BaseModel):
    """健康评分维度 (总分 100)"""
    popularity: int = Field(0, ge=0, le=25, description="流行度 (Stars/Forks/Watchers)")
    activity: int = Field(0, ge=0, le=30, description="活跃度 (更新频率/Commit频率)")
    community: int = Field(0, ge=0, le=20, description="社区 (Contributors/Issues)")
    engineering: int = Field(0, ge=0, le=15, description="工程化 (License/README/Topics)")
    maintenance: int = Field(0, ge=0, le=10, description="维护性 (维护风险)")


class HealthScore(BaseModel):
    score: int = Field(ge=0, le=100)
    dimensions: HealthScoreDimensions


class AIScore(BaseModel):
    """AI 评分 (DeepSeek 生成)"""
    score: int = Field(ge=0, le=100)
    grade: str = Field(pattern=r"^[A-F]$")
    summary: str
    ai_used: bool = Field(True, description="是否使用了 AI 分析")


class AIAnalysis(BaseModel):
    """AI 深度分析 (DeepSeek 生成)"""
    summary: str = Field(description="项目一句话总结")
    strengths: list[str] = Field(default_factory=list, description="优势分析")
    risks: list[str] = Field(default_factory=list, description="风险分析")
    suggestions: list[str] = Field(default_factory=list, description="改进建议")
    ai_used: bool = Field(True, description="是否使用了 AI 分析")


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(ser_json_timedelta="iso8601")

    repository: RepositoryInfo
    languages: LanguageDistribution
    health_score: HealthScore
    ai_score: AIScore
    ai_analysis: AIAnalysis | None = Field(None, description="AI 深度分析")