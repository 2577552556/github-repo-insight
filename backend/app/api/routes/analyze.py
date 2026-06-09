import asyncio
import json

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

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

    # AI Score 从规则引擎的评分结果提取
    ai_score_score = health_score.score
    ai_score = AIScore(
        score=ai_score_score,
        grade=calculate_grade(ai_score_score),
        summary=f"基于 {metrics.contributors_count + metrics.recent_commits_90d} 项指标的仓库健康评估",
        ai_used=True,
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

    return AnalyzeResponse(
        repository=repository_info,
        languages=language_distribution,
        metrics=metrics,
        health_score=health_score,
        ai_score=ai_score,
        ai_analysis=ai_analysis,
    )


async def generate_analysis_stream(url: str):
    """生成分析数据流（SSE 推送）"""
    owner, repo = parse_github_url(url)

    try:
        # STEP 1: 并行获取基础数据
        repository_info, language_distribution = await asyncio.gather(
            github_service.get_repository_info(owner, repo),
            github_service.get_language_distribution(owner, repo),
        )

        # 立即推送 repository
        yield f"data: {json.dumps({'type': 'repository', 'data': repository_info.model_dump()}, ensure_ascii=False)}\n\n"

        # 立即推送 languages
        yield f"data: {json.dumps({'type': 'languages', 'data': language_distribution.model_dump()}, ensure_ascii=False)}\n\n"

        # STEP 2: 获取扩展指标
        metrics = await github_service.get_repository_metrics(owner, repo, days=90)

        # 立即推送 metrics
        yield f"data: {json.dumps({'type': 'metrics', 'data': metrics.model_dump()}, ensure_ascii=False)}\n\n"

        # STEP 3: 计算健康评分
        health_score = health_score_service.calculate(
            repository=repository_info,
            metrics=metrics,
        )

        # 立即推送 health_score
        yield f"data: {json.dumps({'type': 'health_score', 'data': health_score.model_dump()}, ensure_ascii=False)}\n\n"

        # 计算 ai_score
        ai_score_score = health_score.score
        ai_score = AIScore(
            score=ai_score_score,
            grade=calculate_grade(ai_score_score),
            summary=f"基于 {metrics.contributors_count + metrics.recent_commits_90d} 项指标的仓库健康评估",
            ai_used=True,
        )

        # 立即推送 ai_score
        yield f"data: {json.dumps({'type': 'ai_score', 'data': ai_score.model_dump()}, ensure_ascii=False)}\n\n"

        # STEP 4: AI 解读（与前端并行，不阻塞推送）
        ai_analysis = None
        try:
            ai_analysis = await ai_evaluation_service.interpret(
                repository=repository_info,
                languages=language_distribution,
                metrics=metrics,
                health_score=health_score,
            )
        except ValueError:
            pass
        except Exception:
            pass

        # AI 分析完成后推送
        if ai_analysis:
            yield f"data: {json.dumps({'type': 'ai_analysis', 'data': ai_analysis.model_dump()}, ensure_ascii=False)}\n\n"

        # 完成
        yield f"data: {json.dumps({'type': 'complete'}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


@router.post(
    "/analyze/stream",
    summary="Analyze GitHub repository with streaming",
    description="流式推送分析结果，用户可尽快看到已完成的分析内容",
)
async def analyze_repository_stream(request: AnalyzeRequest):
    """流式分析 GitHub 仓库，增量返回结果."""
    return StreamingResponse(
        generate_analysis_stream(request.url),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )