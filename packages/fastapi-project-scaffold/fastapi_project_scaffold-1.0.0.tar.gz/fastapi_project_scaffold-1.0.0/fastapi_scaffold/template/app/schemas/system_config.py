from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class SystemConfigBase(BaseModel):
    """配置基础 Schema"""
    config_key: str = Field(..., min_length=3, max_length=100, description="配置键")
    config_value: Optional[str] = Field(None, description="配置值")
    config_type: str = Field(default="string", description="值类型")
    config_group: str = Field(default="basic", description="配置分组")
    label: str = Field(..., min_length=1, max_length=100, description="显示名称")
    description: Optional[str] = Field(None, description="描述信息")
    is_editable: bool = Field(default=True, description="是否可编辑")
    is_public: bool = Field(default=False, description="是否公开")
    sort_order: int = Field(default=0, description="排序")
    model_config = ConfigDict(from_attributes=True)

class SystemConfigCreate(SystemConfigBase):
    """创建配置 Schema"""
    pass

class SystemConfigUpdate(BaseModel):
    """更新配置 Schema（所有字段可选）"""
    config_value: Optional[str] = None
    config_type: Optional[str] = None
    config_group: Optional[str] = None
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_editable: Optional[bool] = None
    is_public: Optional[bool] = None
    sort_order: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class SystemConfigValueUpdate(BaseModel):
    """仅更新配置值 Schema"""
    value: Optional[str] = Field(None, description="配置值")

    model_config = ConfigDict(from_attributes=True)

class SystemConfigResponse(SystemConfigBase):
    """配置响应 Schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class SystemConfigBatchUpdate(BaseModel):
    """批量更新配置 Schema"""
    updates: dict[str, Optional[str]] = Field(..., description="配置更新字典 {key: value}")

    model_config = ConfigDict(from_attributes=True)
