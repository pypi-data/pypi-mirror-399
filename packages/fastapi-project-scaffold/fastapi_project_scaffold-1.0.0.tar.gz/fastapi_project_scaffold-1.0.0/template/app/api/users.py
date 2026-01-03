from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.common import MessageResponse
from app.schemas.user_admin import UserCreate, UserUpdate, UserAdminResponse
from app.schemas.common import ListResponse
from app.core.dependencies import require_role, require_permission
from app.core.security import get_password_hash

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.get("", response_model=ListResponse[UserAdminResponse], dependencies=[Depends(require_role("admin", "super_admin"))])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    order_by: Optional[str] = Query(None, description="排序字段"),
    order_direction: Optional[str] = Query(None, pattern="^(asc|desc)$", description="排序方向"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/users", "read"))
) -> ListResponse[UserAdminResponse]:
    """查询用户列表"""
    query = db.query(User).filter(User.is_deleted == False)
    
    if search:
        query = query.filter(User.username.contains(search))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 排序
    if order_by and order_direction:
        order_column = getattr(User, order_by, None)
        if order_column is not None:
            if order_direction == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    items = [
        UserAdminResponse(
            id=u.id,
            username=u.username,
            role_id=u.role_id,
            role_name=u.role.name if u.role else None,
            is_active=u.is_active,
            is_deleted=u.is_deleted,
            deleted_at=u.deleted_at,
            created_at=u.created_at,
            last_login_at=u.last_login_at
        ) for u in users
    ]
    
    return ListResponse(total=total, items=items)


@router.post("", response_model=UserAdminResponse, dependencies=[Depends(require_role("admin", "super_admin"))])
def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/users", "create"))
) -> UserAdminResponse:
    """创建用户"""
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    role = db.query(Role).filter(Role.id == user_create.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    new_user = User(
        username=user_create.username,
        password_hash=get_password_hash(user_create.password),
        role_id=user_create.role_id,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserAdminResponse(
        id=new_user.id,
        username=new_user.username,
        role_id=new_user.role_id,
        role_name=new_user.role.name if new_user.role else None,
        is_active=new_user.is_active,
        is_deleted=new_user.is_deleted,
        deleted_at=new_user.deleted_at,
        created_at=new_user.created_at,
        last_login_at=new_user.last_login_at
    )


@router.put("/{user_id}", response_model=UserAdminResponse, dependencies=[Depends(require_role("admin", "super_admin"))])
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/users", "update"))
) -> UserAdminResponse:
    """更新用户"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify your own account"
        )
    
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_update.password:
        user.password_hash = get_password_hash(user_update.password)
    if user_update.role_id is not None:
        role = db.query(Role).filter(Role.id == user_update.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        user.role_id = user_update.role_id
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserAdminResponse(
        id=user.id,
        username=user.username,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        is_active=user.is_active,
        is_deleted=user.is_deleted,
        deleted_at=user.deleted_at,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )


@router.delete("/{user_id}", response_model=MessageResponse, dependencies=[Depends(require_role("admin", "super_admin"))])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/users", "delete"))
) -> MessageResponse:
    """删除用户（软删除）"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    return MessageResponse(message="User deleted successfully")
