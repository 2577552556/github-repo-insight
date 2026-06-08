from fastapi import APIRouter, status

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.github import github_service
from app.services.health_score import health_score_service
from app.services.ai_evaluation import ai_evaluation_service
from app.utils.url_parser import parse_github_url

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze GitHub repository",
    description="Fetch repository information, calculate health score, and perform AI evaluation",
)
async def analyze_repository(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a GitHub repository and return comprehensive health report."""
    owner, repo = parse_github_url(request.url)

    repository_info = await github_service.get_repository_info(owner, repo)
    language_distribution = await github_service.get_language_distribution(owner, repo)
    health_score = health_score_service.calculate(repository_info)
    ai_score = await ai_evaluation_service.evaluate(repository_info, language_distribution)

    return AnalyzeResponse(
        repository=repository_info,
        languages=language_distribution,
        health_score=health_score,
        ai_score=ai_score,
    )