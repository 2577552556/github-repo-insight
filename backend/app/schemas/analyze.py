from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="GitHub repository URL")


class RepositoryInfo(BaseModel):
    name: str
    owner: str
    full_name: str
    description: str | None
    html_url: str
    stars: int = Field(alias="stargazers_count")
    forks: int
    watchers: int = Field(alias="watchers_count")
    open_issues: int = Field(alias="open_issues_count")
    language: str | None
    created_at: str
    updated_at: str
    default_branch: str

    model_config = {"populate_by_name": True}


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


class AnalyzeResponse(BaseModel):
    repository: RepositoryInfo
    languages: LanguageDistribution
    health_score: HealthScore
    ai_score: AIScore