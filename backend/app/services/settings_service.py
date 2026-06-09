"""
Settings Service - 加密凭据管理服务

使用 AES-256-CBC 加密存储凭据
主密钥自动生成并存储在本地文件
"""

from app.core.config import settings
from app.services.database import db_service
from app.services.credential_manager import get_credential_manager, CredentialManager


class SettingsService:
    """配置管理服务（支持运行时更新，加密存储）"""

    def _get_cm(self) -> CredentialManager:
        """获取凭据管理器实例"""
        return get_credential_manager()

    def _encrypt_credential(self, value: str) -> tuple[str, str]:
        """加密凭据"""
        cm = self._get_cm()
        return cm.encrypt(value)

    def _decrypt_credential(self, encrypted_value: str, iv: str) -> str:
        """解密凭据"""
        cm = self._get_cm()
        return cm.decrypt(encrypted_value, iv)

    def get_status(self) -> dict:
        """获取配置状态（检查数据库中是否有凭据）"""
        github_list = db_service.list_credentials("github")
        deepseek_list = db_service.list_credentials("deepseek")
        return {
            "deepseek_configured": len(deepseek_list) > 0,
            "github_configured": len(github_list) > 0,
        }

    def get_decrypted_deepseek_key(self) -> str | None:
        """获取解密的 DeepSeek API Key"""
        cred = db_service.get_credential("deepseek", "api_key")
        if not cred:
            return None
        return self._decrypt_credential(cred["encrypted_value"], cred["iv"])

    def get_decrypted_github_token(self) -> str | None:
        """获取解密的 GitHub Token"""
        cred = db_service.get_credential("github", "token")
        if not cred:
            return None
        return self._decrypt_credential(cred["encrypted_value"], cred["iv"])

    def update_deepseek_key(self, api_key: str | None) -> dict:
        """更新 DeepSeek API Key（加密存储）"""
        if api_key:
            encrypted_value, iv = self._encrypt_credential(api_key)
            db_service.save_credential("deepseek", "api_key", encrypted_value, iv)
            # 同步更新运行时 settings
            settings.DEEPSEEK_API_KEY = api_key
        else:
            db_service.delete_credential("deepseek", "api_key")
            settings.DEEPSEEK_API_KEY = None

        return self.get_status()

    def update_github_token(self, token: str | None) -> dict:
        """更新 GitHub Token（加密存储）"""
        if token:
            encrypted_value, iv = self._encrypt_credential(token)
            db_service.save_credential("github", "token", encrypted_value, iv)
            # 同步更新运行时 settings
            settings.GITHUB_TOKEN = token
        else:
            db_service.delete_credential("github", "token")
            settings.GITHUB_TOKEN = None

        return self.get_status()


settings_service = SettingsService()