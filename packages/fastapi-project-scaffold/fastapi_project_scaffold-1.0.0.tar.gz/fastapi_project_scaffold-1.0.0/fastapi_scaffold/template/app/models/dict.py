"""
字典管理模型
包含字典类型和字典数据两个表
"""
from sqlalchemy import String, Boolean, Text, JSON, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import datetime
from typing import Optional


class DictType(Base):
    """字典类型表 - 管理字典分类"""
    __tablename__ = "dict_types"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 权限控制字段
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # 系统预置
    allow_add: Mapped[bool] = mapped_column(Boolean, default=True)  # 允许新增
    allow_delete: Mapped[bool] = mapped_column(Boolean, default=True)  # 允许删除
    
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    __table_args__ = (
        Index('idx_dict_type_code', 'type_code'),
        Index('idx_dict_type_active', 'is_active'),
    )


class DictData(Base):
    """字典数据表 - 存储具体字典项"""
    __tablename__ = "dict_data"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type_code: Mapped[str] = mapped_column(ForeignKey("dict_types.type_code"), nullable=False)
    dict_code: Mapped[str] = mapped_column(String(50), nullable=False)
    dict_label: Mapped[str] = mapped_column(String(100), nullable=False)
    dict_value: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_code: Mapped[Optional[str]] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(default=0)
    css_class: Mapped[Optional[str]] = mapped_column(String(50))
    is_default: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    remark: Mapped[Optional[str]] = mapped_column(Text)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    __table_args__ = (
        UniqueConstraint('type_code', 'dict_code', name='uk_type_code'),
        Index('idx_dict_data_type', 'type_code'),
        Index('idx_dict_data_code', 'dict_code'),
        Index('idx_dict_data_active', 'is_active'),
        Index('idx_dict_data_parent', 'parent_code'),
    )
