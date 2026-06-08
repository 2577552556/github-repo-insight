from pydantic import BaseModel

from fastapi import APIRouter

from app.services.settings_service import settings_service


router = APIRouter()


class SettingsStatus(BaseModel):
    deepseek_configured: bool
    github_configured: bool


class UpdateSettingsRequest(BaseModel):
    deepseek_api_key: str | None = None
    github_token: str | None = None


@router.get("/settings", response_model=SettingsStatus, tags=["settings"])
async def get_settings() -> SettingsStatus:
    """获取当前配置状态"""
    status = settings_service.get_status()
    return SettingsStatus(**status)


@router.put("/settings", response_model=SettingsStatus, tags=["settings"])
async def update_settings(body: UpdateSettingsRequest) -> SettingsStatus:
    """更新配置（实时生效）"""
    # 更新 DeepSeek API Key
    if body.deepseek_api_key is not None:
        settings_service.update_deepseek_key(body.deepseek_api_key)

    # 更新 GitHub Token
    if body.github_token is not None:
        settings_service.update_github_token(body.github_token)

    return SettingsStatus(**settings_service.get_status())