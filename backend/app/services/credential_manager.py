"""
Credential Manager - AES 加密凭据管理服务

使用 AES-256-CBC 加密存储凭据
主密钥从环境变量 CREDENTIAL_MASTER_KEY 读取，不落盘
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Optional


class CredentialManager:
    """AES 加密凭据管理器"""

    def __init__(self, master_key: Optional[str] = None):
        """初始化加密管理器

        Args:
            master_key: 主密钥，如果为 None 则从环境变量读取
        """
        self._master_key = master_key or os.environ.get("CREDENTIAL_MASTER_KEY")
        if not self._master_key:
            raise ValueError("CREDENTIAL_MASTER_KEY 环境变量未设置")
        self._key_bytes = self._derive_key(self._master_key)

    @staticmethod
    def _derive_key(master_key: str) -> bytes:
        """从主密钥派生 AES-256 密钥

        Args:
            master_key: 主密钥字符串

        Returns:
            32 字节的 AES-256 密钥
        """
        return hashlib.sha256(master_key.encode()).digest()

    def encrypt(self, plaintext: str) -> tuple[str, str]:
        """加密凭据

        Args:
            plaintext: 明文凭据

        Returns:
            (密文, IV) 元组，均为 Base64 编码字符串
        """
        # 生成随机 IV
        iv = os.urandom(16)

        # AES-256-CBC 加密
        cipher = Cipher(
            algorithms.AES(self._key_bytes),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # PKCS7 Padding
        padding_length = 16 - (len(plaintext.encode('utf-8')) % 16)
        padded_data = plaintext.encode('utf-8') + bytes([padding_length] * padding_length)

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return (
            base64.b64encode(ciphertext).decode('utf-8'),
            base64.b64encode(iv).decode('utf-8')
        )

    def decrypt(self, ciphertext: str, iv: str) -> str:
        """解密凭据

        Args:
            ciphertext: Base64 编码的密文
            iv: Base64 编码的 IV

        Returns:
            解密后的明文
        """
        cipher_data = base64.b64decode(ciphertext)
        iv_bytes = base64.b64decode(iv)

        cipher = Cipher(
            algorithms.AES(self._key_bytes),
            modes.CBC(iv_bytes),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(cipher_data) + decryptor.finalize()

        # 移除 PKCS7 Padding
        padding_length = padded_plaintext[-1]
        plaintext = padded_plaintext[:-padding_length].decode('utf-8')

        return plaintext

    @staticmethod
    def generate_master_key() -> str:
        """生成随机主密钥

        Returns:
            32 字节随机字符串，可作为主密钥使用
        """
        return base64.b64encode(os.urandom(32)).decode('utf-8')


# 全局实例（延迟初始化）
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """获取凭据管理器单例

    Returns:
        CredentialManager 实例

    Raises:
        ValueError: 如果 CREDENTIAL_MASTER_KEY 未设置
    """
    global _credential_manager
    if _credential_manager is None:
        master_key = os.environ.get("CREDENTIAL_MASTER_KEY")
        if not master_key:
            # 尝试从配置文件读取（但主密钥不应该持久化存储）
            from app.core.config import settings
            master_key = getattr(settings, 'CREDENTIAL_MASTER_KEY', None)

        if not master_key:
            raise ValueError("CREDENTIAL_MASTER_KEY 环境变量未设置")

        _credential_manager = CredentialManager(master_key)

    return _credential_manager