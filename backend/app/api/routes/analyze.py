from fastapi import APIRouter, HTTPException, status

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

    # 获取基础数据
    repository_info = await github_service.get_repository_info(owner, repo)
    language_distribution = await github_service.get_language_distribution(owner, repo)

    # 获取额外数据
    recent_commits = await github_service.get_recent_commits_count(owner, repo, days=30)
    contributors_count = await github_service.get_contributors_count(owner, repo)

    # 计算健康评分
    health_score = health_score_service.calculate(
        repository=repository_info,
        recent_commits=recent_commits,
        contributors_count=contributors_count,
    )

    # AI 快速评分
    try:
        ai_score = await ai_evaluation_service.evaluate_quick(
            repository=repository_info,
            recent_commits=recent_commits,
            contributors_count=contributors_count,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 评分服务不可用: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 评分服务调用失败: {str(e)}"
        )

    # AI 深度分析
    try:
        ai_analysis = await ai_evaluation_service.analyze(
            repository=repository_info,
            languages=language_distribution,
            recent_commits=recent_commits,
            contributors_count=contributors_count,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 分析服务不可用: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 分析服务调用失败: {str(e)}"
        )

    return AnalyzeResponse(
        repository=repository_info,
        languages=language_distribution,
        health_score=health_score,
        ai_score=ai_score,
        ai_analysis=ai_analysis,
    )