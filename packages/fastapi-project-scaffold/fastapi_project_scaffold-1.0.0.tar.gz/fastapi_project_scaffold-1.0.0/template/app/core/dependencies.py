from typing import List
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.casbin_enforcer import check_permission
from app.models.user import User
from app.database import get_db


def get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


def require_active(current_user: User = Depends(get_current_user)) -> User:
    """要求用户处于激活状态"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


def get_current_active_user(current_user: User = Depends(require_active)) -> User:
    """获取当前激活用户"""
    return current_user


def require_role(*allowed_roles: str):
    """路由级角色验证装饰器"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned"
            )
        
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


def require_permission(resource: str, action: str):
    """Casbin细粒度权限验证装饰器"""
    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned"
            )
        
        if not check_permission(current_user.role.name, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} on {resource}"
            )
        
        return current_user
    
    return permission_checker
