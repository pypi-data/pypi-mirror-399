from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, TokenResponse, UserResponse, RefreshTokenRequest
from app.core.security import verify_password, create_access_token, get_current_user
from app.utils.refresh_token import (
    create_refresh_token, 
    verify_refresh_token, 
    revoke_refresh_token,
    revoke_all_user_tokens
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """用户登录"""
    user = db.query(User).filter(
        User.username == credentials.username,
        User.is_deleted == False
    ).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    
    # 创建 Access Token 和 Refresh Token
    access_token = create_access_token(
        data={"sub": user.username},
        role_name=user.role.name if user.role else None,
        password_changed_at=user.password_changed_at
    )
    refresh_token = create_refresh_token(db, user)
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )
    
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token,
        user=user_response
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """刷新 Access Token"""
    # 验证 Refresh Token
    user = verify_refresh_token(db, request.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # 生成新的 Access Token
    access_token = create_access_token(
        data={"sub": user.username},
        role_name=user.role.name if user.role else None,
        password_changed_at=user.password_changed_at
    )
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # 返回原 Refresh Token
        user=user_response
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MessageResponse:
    """登出（当前设备）"""
    revoke_refresh_token(db, request.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post("/logout-all", response_model=MessageResponse)
def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MessageResponse:
    """登出所有设备"""
    revoke_all_user_tokens(db, current_user.id)
    return MessageResponse(message="Logged out from all devices successfully")
