"""
Credential Manager - AES 加密凭据管理服务

使用 AES-256-CBC 加密存储凭据
主密钥自动生成并存储在本地文件，无需手动配置
"""

import os
import base64
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Optional


# 密钥文件路径
_CREDENTIAL_KEY_FILE = Path(__file__).parent.parent.parent / "data" / ".credential_key"


class CredentialManager:
    """AES 加密凭据管理器"""

    def __init__(self, master_key: str):
        """初始化加密管理器

        Args:
            master_key: 主密钥字符串
        """
        self._master_key = master_key
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


def _load_or_create_master_key() -> str:
    """加载或创建主密钥

    首次启动时自动生成主密钥并保存到本地文件
    后续启动从文件读取

    Returns:
        主密钥字符串
    """
    global _CREDENTIAL_KEY_FILE

    # 确保目录存在
    _CREDENTIAL_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 检查密钥文件是否存在
    if _CREDENTIAL_KEY_FILE.exists():
        key = _CREDENTIAL_KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key

    # 生成新密钥
    key = CredentialManager.generate_master_key()
    _CREDENTIAL_KEY_FILE.write_text(key, encoding="utf-8")

    # 设置文件权限（仅所有者可读写）
    try:
        os.chmod(_CREDENTIAL_KEY_FILE, 0o600)
    except Exception:
        pass  # Windows 可能不支持

    return key


# 全局实例（延迟初始化）
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """获取凭据管理器单例

    自动加载或创建主密钥，无需手动配置

    Returns:
        CredentialManager 实例
    """
    global _credential_manager
    if _credential_manager is None:
        master_key = _load_or_create_master_key()
        _credential_manager = CredentialManager(master_key)

    return _credential_manager