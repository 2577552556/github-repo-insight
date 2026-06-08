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


class LanguageDistribution(BaseModel):
    languages: dict[str, float] = Field(
        ..., description="Language distribution as percentages"
    )


class HealthScoreDimensions(BaseModel):
    popularity: int = Field(..., ge=0, le=25)
    activity: int = Field(..., ge=0, le=25)
    community: int = Field(..., ge=0, le=25)
    maintenance: int = Field(..., ge=0, le=25)


class HealthScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    dimensions: HealthScoreDimensions


class AIScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    grade: str = Field(..., pattern=r"^[A-F]$")
    summary: str
    ai_used: bool = Field(True, description="是否使用了 AI 分析，false 表示使用规则评估")


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(ser_json_timedelta="iso8601")

    repository: RepositoryInfo
    languages: LanguageDistribution
    health_score: HealthScore
    ai_score: AIScore