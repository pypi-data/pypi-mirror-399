from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.example import Example
from app.schemas.example import ExampleCreate, ExampleUpdate, ExampleResponse
from app.schemas.common import ListResponse
from app.schemas.common import MessageResponse
from app.core.dependencies import get_current_active_user

# TODO: 这是示例API，请根据业务需求修�?

router = APIRouter(prefix="/api/examples", tags=["Examples"])


@router.get("", response_model=ListResponse[ExampleResponse])
def list_examples(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ListResponse[ExampleResponse]:
    """查询示例列表"""
    query = db.query(Example).filter(Example.user_id == current_user.id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return ListResponse(
        total=total,
        items=[ExampleResponse.model_validate(item) for item in items]
    )


@router.post("", response_model=ExampleResponse)
def create_example(
    example_create: ExampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ExampleResponse:
    """创建示例"""
    new_example = Example(
        title=example_create.title,
        content=example_create.content,
        user_id=current_user.id
    )
    
    db.add(new_example)
    db.commit()
    db.refresh(new_example)
    
    return ExampleResponse.model_validate(new_example)


@router.put("/{example_id}", response_model=ExampleResponse)
def update_example(
    example_id: int,
    example_update: ExampleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ExampleResponse:
    """更新示例"""
    example = db.query(Example).filter(
        Example.id == example_id,
        Example.user_id == current_user.id
    ).first()
    
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found"
        )
    
    if example_update.title is not None:
        example.title = example_update.title
    if example_update.content is not None:
        example.content = example_update.content
    
    db.commit()
    db.refresh(example)
    
    return ExampleResponse.model_validate(example)


@router.delete("/{example_id}", response_model=MessageResponse)
def delete_example(
    example_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MessageResponse:
    """删除示例"""
    example = db.query(Example).filter(
        Example.id == example_id,
        Example.user_id == current_user.id
    ).first()
    
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found"
        )
    
    db.delete(example)
    db.commit()
    
    return MessageResponse(message="Example deleted successfully")
