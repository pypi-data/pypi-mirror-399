import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.refresh_token import RefreshToken


def generate_refresh_token() -> str:
    """生成随机 refresh token"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """对 token 进行哈希"""
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(db: Session, user: User) -> str:
    """创建并保存 refresh token"""
    token = generate_refresh_token()
    token_hash = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return token


def verify_refresh_token(db: Session, token: str) -> Optional[User]:
    """验证 refresh token 并返回用户"""
    token_hash = hash_token(token)
    
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not db_token:
        return None
    
    user = db.query(User).filter(
        User.id == db_token.user_id,
        User.is_active == True,
        User.is_deleted == False
    ).first()
    
    return user


def revoke_refresh_token(db: Session, token: str) -> bool:
    """撤销 refresh token"""
    token_hash = hash_token(token)
    
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()
    
    if db_token:
        db_token.is_revoked = True
        db.commit()
        return True
    
    return False


def revoke_all_user_tokens(db: Session, user_id: int) -> int:
    """撤销用户的所有 refresh token"""
    count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    db.commit()
    return count


def cleanup_expired_tokens(db: Session) -> int:
    """清理过期的 token（可定期执行）"""
    count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    db.commit()
    return count
