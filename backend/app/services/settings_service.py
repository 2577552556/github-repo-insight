import json
from pathlib import Path

from app.core.config import settings


class SettingsService:
    """配置管理服务（支持运行时更新）"""

    SETTINGS_DIR = Path(__file__).parent.parent.parent / "data"
    SETTINGS_FILE = SETTINGS_DIR / "settings.json"

    def __init__(self):
        """确保数据目录存在"""
        self.SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> dict:
        """获取配置状态（优先从 settings.json 读取）"""
        data = self._load_from_file()
        # 优先从 settings.json 读取，如果没有配置才 fallback 到 .env
        deepseek_key = data.get("deepseek_api_key") or settings.DEEPSEEK_API_KEY
        github_token = data.get("github_token") or settings.GITHUB_TOKEN
        return {
            "deepseek_configured": bool(deepseek_key),
            "github_configured": bool(github_token),
        }

    def _load_from_file(self) -> dict:
        """从 JSON 文件加载配置"""
        if self.SETTINGS_FILE.exists():
            return json.loads(self.SETTINGS_FILE.read_text(encoding="utf-8"))
        return {}

    def _save_to_file(self, data: dict) -> None:
        """保存配置到 JSON 文件（原子操作）"""
        self.SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        temp_file = self.SETTINGS_FILE.with_suffix(".tmp")
        temp_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_file.replace(self.SETTINGS_FILE)

    def update_deepseek_key(self, api_key: str | None) -> dict:
        """更新 DeepSeek API Key（实时生效）"""
        # 1. 持久化到 JSON 文件
        data = self._load_from_file()
        if api_key:
            data["deepseek_api_key"] = api_key
        else:
            data.pop("deepseek_api_key", None)
        self._save_to_file(data)

        # 2. 运行时更新 settings 对象
        settings.DEEPSEEK_API_KEY = api_key or None

        # 3. 返回新状态
        return self.get_status()

    def update_github_token(self, token: str | None) -> dict:
        """更新 GitHub Token（实时生效）"""
        # 1. 持久化到 JSON 文件
        data = self._load_from_file()
        if token:
            data["github_token"] = token
        else:
            data.pop("github_token", None)
        self._save_to_file(data)

        # 2. 运行时更新 settings 对象
        settings.GITHUB_TOKEN = token or None

        # 3. 返回新状态
        return self.get_status()


settings_service = SettingsService()