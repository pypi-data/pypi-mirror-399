"""
枚举管理 API
提供系统固定枚举的查询接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Type, List
from enum import Enum

from app.models.enums import (
    Gender,
    PersonnelStatus,
    TrainingSubjectStatus,
    TrainingTaskStatus,
    QuestionType
)

router = APIRouter(prefix="/api/enums", tags=["Enums"])


# ==================== 响应模型 ====================

class EnumOption(BaseModel):
    """枚举选项"""
    value: str = Field(..., description="枚举值")
    label: str = Field(..., description="显示标签")


class EnumTypeInfo(BaseModel):
    """枚举类型信息"""
    name: str = Field(..., description="枚举名称")
    count: int = Field(..., description="选项数量")


# ==================== 枚举注册表 ====================

ENUM_REGISTRY: Dict[str, Type[Enum]] = {
    "Gender": Gender,
    "PersonnelStatus": PersonnelStatus,
    "TrainingSubjectStatus": TrainingSubjectStatus,
    "TrainingTaskStatus": TrainingTaskStatus,
    "QuestionType": QuestionType,
}


# ==================== 中文标签映射 ====================

ENUM_LABELS: Dict[str, Dict[str, str]] = {
    "Gender": {
        "male": "男",
        "female": "女"
    },
    "PersonnelStatus": {
        "active": "在职",
        "resigned": "离职"
    },
    "TrainingSubjectStatus": {
        "draft": "草稿",
        "active": "启用",
        "archived": "归档"
    },
    "TrainingTaskStatus": {
        "draft": "草稿",
        "started": "启动",
        "training": "训练",
        "completed": "完成",
        "cancelled": "取消"
    },
    "QuestionType": {
        "choice": "选择题",
        "judgment": "判断题",
        "answer": "问答题"
    }
}


# ==================== API 端点 ====================

@router.get("/{enum_name}", response_model=List[EnumOption], summary="获取枚举选项")
def get_enum_options(enum_name: str) -> List[EnumOption]:
    """
    获取指定枚举的所有选项
    
    Args:
        enum_name: 枚举代码，如 'Gender', 'PersonnelStatus'
        
    Returns:
        枚举选项列表，包含 value 和 label
    """
    if enum_name not in ENUM_REGISTRY:
        raise HTTPException(404, f"枚举类型 '{enum_name}' 不存在")
    
    enum_class = ENUM_REGISTRY[enum_name]
    labels = ENUM_LABELS.get(enum_name, {})
    
    options: List[EnumOption] = []
    for item in enum_class:
        options.append(EnumOption(
            value=item.value,
            label=labels.get(item.value, item.name)
        ))
    
    return options


@router.get("", response_model=List[EnumTypeInfo], summary="列出所有枚举类型")
def list_all_enums() -> List[EnumTypeInfo]:
    """
    列出系统中所有可用的枚举类型
    
    Returns:
        枚举类型列表，包含 name 和 count
    """
    enum_list: List[EnumTypeInfo] = []
    for name, enum_class in ENUM_REGISTRY.items():
        enum_list.append(EnumTypeInfo(
            name=name,
            count=len(list(enum_class))
        ))
    
    return enum_list
