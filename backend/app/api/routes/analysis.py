"""
Analysis Workspace - History Records API

历史记录 CRUD 端点。
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.schemas.analyze import (
    AnalyzeRequest,
    AnalysisRecord,
    AnalysisRecordSummary,
)
from app.services.database import db_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="创建新分析记录",
)
async def create_analysis(request: AnalyzeRequest) -> dict:
    """创建新分析记录（立即返回 ID，后台异步执行）"""
    # 从 URL 解析 owner 和 repo
    url = request.url.rstrip("/")
    if url.endswith("/"):
        url = url[:-1]

    parts = url.split("/")
    if len(parts) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的仓库 URL",
        )

    # 获取 owner 和 repo
    if "github.com" in parts:
        idx = parts.index("github.com")
        owner = parts[idx + 1]
        repo = parts[idx + 2]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的仓库 URL",
        )

    full_name = f"{owner}/{repo}"
    repository_name = repo

    # 创建记录
    record_id = db_service.create_analysis_record(
        repository_url=request.url,
        repository_name=repository_name,
        owner=owner,
        full_name=full_name,
    )

    return {
        "id": record_id,
        "repository_url": request.url,
        "repository_name": repository_name,
        "owner": owner,
        "full_name": full_name,
        "status": "processing",
    }


@router.get(
    "/history",
    response_model=list[AnalysisRecordSummary],
    summary="获取历史记录列表",
)
async def get_analysis_history(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
) -> list[dict]:
    """获取历史记录列表（按时间倒序）"""
    records = db_service.get_analysis_history(
        skip=skip,
        limit=limit,
        search=search,
    )
    return records


@router.get(
    "/{record_id}",
    response_model=AnalysisRecord,
    summary="获取单条分析记录",
)
async def get_analysis(record_id: str) -> dict:
    """获取单条分析记录的完整结果"""
    record = db_service.get_analysis_record(record_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"记录 {record_id} 不存在",
        )

    # 返回完整记录（包括 result_json）
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除分析记录",
)
async def delete_analysis(record_id: str):
    """删除分析记录"""
    success = db_service.delete_analysis_record(record_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"记录 {record_id} 不存在",
        )


@router.post(
    "/{record_id}/reanalyze",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="重新分析仓库",
)
async def reanalyze_repository(record_id: str) -> dict:
    """重新分析仓库（会创建新记录）"""
    # 获取原记录
    record = db_service.get_analysis_record(record_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"记录 {record_id} 不存在",
        )

    # 创建新分析
    new_record_id = db_service.create_analysis_record(
        repository_url=record["repository_url"],
        repository_name=record["repository_name"],
        owner=record["owner"],
        full_name=record["full_name"],
    )

    return {
        "id": new_record_id,
        "repository_url": record["repository_url"],
        "repository_name": record["repository_name"],
        "status": "processing",
    }