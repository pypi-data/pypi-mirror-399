from sqlalchemy import String, Text, Integer, Boolean, Enum as SQLEnum, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database import Base


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_configs"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 配置键（唯一标识，点分命名）
    config_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    # 配置值（文本存储）
    config_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 值类型
    config_type: Mapped[str] = mapped_column(
        SQLEnum('string', 'number', 'boolean', 'json', name='config_type_enum'),
        default='string',
        nullable=False
    )
    
    # 配置分组
    config_group: Mapped[str] = mapped_column(
        String(50),
        default='basic',
        index=True,
        nullable=False
    )
    
    # 显示名称
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 描述信息
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 是否可编辑
    is_editable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 是否公开（前端可访问）
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    
    # 排序
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now(), nullable=True)
    
    # 复合索引
    __table_args__ = (
        Index('idx_group_public', 'config_group', 'is_public'),
        Index('idx_public_group', 'is_public', 'config_group'),
    )
