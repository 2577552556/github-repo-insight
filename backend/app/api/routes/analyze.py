import asyncio

from fastapi import APIRouter, HTTPException, status

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, AIScore
from app.services.github import github_service
from app.services.health_score import health_score_service, calculate_grade
from app.services.ai_evaluation import ai_evaluation_service
from app.utils.url_parser import parse_github_url

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze GitHub repository",
    description="Fetch repository information, calculate health score, and perform AI interpretation",
)
async def analyze_repository(request: AnalyzeRequest) -> AnalyzeResponse:
    """分析 GitHub 仓库并返回健康体检报告."""
    owner, repo = parse_github_url(request.url)

    # 并行获取基础数据（两个独立的 GitHub API 调用）
    repository_info, language_distribution = await asyncio.gather(
        github_service.get_repository_info(owner, repo),
        github_service.get_language_distribution(owner, repo),
    )

    # 获取扩展指标（用于评分）
    metrics = await github_service.get_repository_metrics(owner, repo, days=90)

    # 规则引擎计算健康评分
    health_score = health_score_service.calculate(
        repository=repository_info,
        metrics=metrics,
    )

    # AI 解读（基于规则引擎的评分结果，失败不影响主体返回）
    ai_analysis = None
    try:
        ai_analysis = await ai_evaluation_service.interpret(
            repository=repository_info,
            languages=language_distribution,
            metrics=metrics,
            health_score=health_score,
        )
    except ValueError:
        # API Key 未配置，ai_analysis 为 None
        pass
    except Exception:
        # AI 服务调用失败，ai_analysis 为 None，主体数据仍正常返回
        pass

    # AI Score 从规则引擎的评分结果提取
    ai_score_score = health_score.score
    ai_score = AIScore(
        score=ai_score_score,
        grade=calculate_grade(ai_score_score),
        summary=f"基于 {metrics.contributors_count + metrics.recent_commits_90d} 项指标的仓库健康评估",
        ai_used=True,
    )

    return AnalyzeResponse(
        repository=repository_info,
        languages=language_distribution,
        metrics=metrics,
        health_score=health_score,
        ai_score=ai_score,
        ai_analysis=ai_analysis,
    )