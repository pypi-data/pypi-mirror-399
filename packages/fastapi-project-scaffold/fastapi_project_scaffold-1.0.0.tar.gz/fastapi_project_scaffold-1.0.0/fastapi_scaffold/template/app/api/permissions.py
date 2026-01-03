from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.schemas.common import ListResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import require_role, require_permission

router = APIRouter(prefix="/api/permissions", tags=["Permission Management"])


@router.get("", response_model=ListResponse[PermissionResponse], dependencies=[Depends(require_role("super_admin"))])
def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/permissions", "read"))
) -> ListResponse[PermissionResponse]:
    """查询权限列表"""
    total = db.query(Permission).count()
    permissions = db.query(Permission).offset(skip).limit(limit).all()
    
    return ListResponse(
        total=total,
        items=[PermissionResponse.model_validate(p) for p in permissions]
    )


@router.post("", response_model=PermissionResponse, dependencies=[Depends(require_role("super_admin"))])
def create_permission(
    permission_create: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/permissions", "create"))
) -> PermissionResponse:
    """创建权限"""
    existing = db.query(Permission).filter(
        Permission.resource == permission_create.resource,
        Permission.action == permission_create.action
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )
    
    new_permission = Permission(
        resource=permission_create.resource,
        action=permission_create.action,
        description=permission_create.description
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return PermissionResponse.model_validate(new_permission)


@router.put("/{permission_id}", response_model=PermissionResponse, dependencies=[Depends(require_role("super_admin"))])
def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/permissions", "update"))
) -> PermissionResponse:
    """更新权限"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    if permission_update.description is not None:
        permission.description = permission_update.description
    
    db.commit()
    db.refresh(permission)
    
    return PermissionResponse.model_validate(permission)


@router.delete("/{permission_id}", response_model=MessageResponse, dependencies=[Depends(require_role("super_admin"))])
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("/api/permissions", "delete"))
) -> MessageResponse:
    """删除权限"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    db.delete(permission)
    db.commit()
    
    return MessageResponse(message="Permission deleted successfully")
