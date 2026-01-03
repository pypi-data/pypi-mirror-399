from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.common import MessageResponse
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse,
    RoleWithPermissions, RolePermissionUpdate
)
from app.schemas.common import ListResponse
from app.core.dependencies import require_role, require_permission
from app.core.casbin_enforcer import sync_policies_from_db

router = APIRouter(prefix="/api/roles", tags=["Role Management"])


@router.get("", response_model=ListResponse[RoleResponse], dependencies=[Depends(require_role("admin", "super_admin"))])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/roles", "read"))
) -> ListResponse[RoleResponse]:
    """查询角色列表"""
    total = db.query(Role).count()
    roles = db.query(Role).offset(skip).limit(limit).all()
    
    return ListResponse(
        total=total,
        items=[RoleResponse.model_validate(role) for role in roles]
    )


@router.get("/{role_id}", response_model=RoleWithPermissions, dependencies=[Depends(require_role("super_admin"))])
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/roles", "read"))
) -> RoleWithPermissions:
    """获取角色详情（含权限列表）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    permission_ids = [p.id for p in role.permissions]
    
    return RoleWithPermissions(
        id=role.id,
        name=role.name,
        display_name=role.display_name,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permission_ids=permission_ids
    )


@router.post("", response_model=RoleResponse, dependencies=[Depends(require_role("super_admin"))])
def create_role(
    role_create: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/roles", "create"))
) -> RoleResponse:
    """创建角色"""
    existing_role = db.query(Role).filter(Role.name == role_create.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    new_role = Role(
        name=role_create.name,
        display_name=role_create.display_name,
        description=role_create.description,
        is_system=False
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return RoleResponse.model_validate(new_role)


@router.put("/{role_id}", response_model=RoleResponse, dependencies=[Depends(require_role("super_admin"))])
def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/roles", "update"))
) -> RoleResponse:
    """更新角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system role"
        )
    
    if role_update.display_name is not None:
        role.display_name = role_update.display_name
    if role_update.description is not None:
        role.description = role_update.description
    
    db.commit()
    db.refresh(role)
    
    return RoleResponse.model_validate(role)


@router.delete("/{role_id}", response_model=MessageResponse, dependencies=[Depends(require_role("super_admin"))])
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/roles", "delete"))
) -> MessageResponse:
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system role"
        )
    
    user_count = db.query(User).filter(User.role_id == role_id).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role: {user_count} users are assigned to this role"
        )
    
    db.delete(role)
    db.commit()
    
    return MessageResponse(message="Role deleted successfully")


@router.put("/{role_id}/permissions", response_model=RoleWithPermissions, dependencies=[Depends(require_role("super_admin"))])
def update_role_permissions(
    role_id: int,
    permission_update: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/roles", "update"))
) -> RoleWithPermissions:
    """更新角色权限"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    permissions = db.query(Permission).filter(Permission.id.in_(permission_update.permission_ids)).all()
    if len(permissions) != len(permission_update.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some permissions not found"
        )
    
    role.permissions = permissions
    db.commit()
    db.refresh(role)
    
    # 同步权限到Casbin
    sync_policies_from_db(db)
    
    permission_ids = [p.id for p in role.permissions]
    
    return RoleWithPermissions(
        id=role.id,
        name=role.name,
        display_name=role.display_name,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permission_ids=permission_ids
    )
