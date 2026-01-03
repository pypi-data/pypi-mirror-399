from typing import cast
from cryptography.fernet import Fernet
from app.core.config import settings


def get_cipher() -> Fernet:
    """获取加密器"""
    key = settings.ENCRYPTION_KEY.encode()
    if len(key) != 32:
        raise ValueError("ENCRYPTION_KEY must be exactly 32 bytes long")
    
    # 生成Fernet密钥（Base64编码）
    from base64 import urlsafe_b64encode
    fernet_key = urlsafe_b64encode(key)
    return Fernet(fernet_key)


def encrypt_data(data: str) -> str:
    """AES-256加密"""
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(data.encode())
    # Fernet.encrypt returns bytes, decode to str
    return cast(str, encrypted_bytes.decode())


def decrypt_data(encrypted_data: str) -> str:
    """AES-256解密"""
    cipher = get_cipher()
    decrypted_bytes = cipher.decrypt(encrypted_data.encode())
    # Fernet.decrypt returns bytes, decode to str
    return cast(str, decrypted_bytes.decode())
