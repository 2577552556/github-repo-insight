import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GITHUB_TOKEN: str | None = None
    OPENAI_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    CREDENTIAL_MASTER_KEY: str | None = None
    GITHUB_API_URL: str = "https://api.github.com"
    OPENAI_API_URL: str = "https://api.openai.com/v1"
    DEEPSEEK_API_URL: str = "https://api.deepseek.com"

    timeout: int = 30

    def reload_from_file(self, json_path: Path) -> None:
        """从 JSON 文件加载配置（运行时更新）"""
        if json_path.exists():
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if "deepseek_api_key" in data:
                self.DEEPSEEK_API_KEY = data["deepseek_api_key"] or None


settings = Settings()