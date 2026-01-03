"""
字典管理 Schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Any
from datetime import datetime
import json

# ========== 强类型定义 ==========

class DictExtraData(BaseModel):
    """字典扩展数据（强类型）"""
    icon: Optional[str] = Field(None, description="图标")
    color: Optional[str] = Field(None, description="颜色")
    link: Optional[str] = Field(None, description="链接")
    
    model_config = ConfigDict(extra="allow", from_attributes=True)

class ReferenceItem(BaseModel):
    """引用项（强类型）"""
    table: str = Field(..., description="表名")
    field: str = Field(..., description="字段名")
    count: int = Field(..., ge=0, description="引用数量")
    
    model_config = ConfigDict(from_attributes=True)

# ========== 字典类型 Schemas ==========

class DictTypeBase(BaseModel):
    """字典类型基础模型"""
    type_code: str = Field(..., min_length=1, max_length=50, description="类型编码")
    type_name: str = Field(..., min_length=1, max_length=100, description="类型名称")
    description: Optional[str] = Field(None, description="描述")
    is_system: bool = Field(False, description="是否系统预置")
    allow_add: bool = Field(True, description="是否允许新增")
    allow_delete: bool = Field(True, description="是否允许删除")
    is_active: bool = Field(True, description="是否启用")

    model_config = ConfigDict(from_attributes=True)

class DictTypeCreate(DictTypeBase):
    """创建字典类型"""
    pass

class DictTypeUpdate(BaseModel):
    """更新字典类型"""
    type_name: Optional[str] = Field(None, min_length=1, max_length=100, description="类型名称")
    description: Optional[str] = Field(None, description="描述")
    is_system: Optional[bool] = Field(None, description="是否系统预置")
    allow_add: Optional[bool] = Field(None, description="是否允许新增")
    allow_delete: Optional[bool] = Field(None, description="是否允许删除")
    is_active: Optional[bool] = Field(None, description="是否启用")

    model_config = ConfigDict(from_attributes=True)

class DictTypeResponse(DictTypeBase):
    """字典类型响应"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ========== 字典数据 Schemas ==========

class DictDataBase(BaseModel):
    """字典数据基础模型"""
    type_code: str = Field(..., max_length=50, description="类型编码")
    dict_code: str = Field(..., max_length=50, description="字典编码")
    dict_label: str = Field(..., max_length=100, description="字典标签")
    dict_value: str = Field(..., max_length=100, description="字典值")
    parent_code: Optional[str] = Field(None, max_length=50, description="父编码")
    sort_order: int = Field(0, description="排序")
    css_class: Optional[str] = Field(None, max_length=50, description="CSS类名")
    is_default: bool = Field(False, description="是否默认")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, description="备注")
    extra_data: Optional[DictExtraData] = Field(None, description="扩展数据")
    
    @field_validator('extra_data', mode='before')
    @classmethod
    def parse_extra_data(cls, v: Any) -> Optional[DictExtraData]:
        """解析JSON字符串为DictExtraData"""
        if isinstance(v, str):
            data = json.loads(v) if v else None
            return DictExtraData(**data) if data else None
        if isinstance(v, dict):
            return DictExtraData(**v)
        if v is None:
            return None
        return None  # 其他类型返回 None

    model_config = ConfigDict(from_attributes=True)

class DictDataCreate(DictDataBase):
    """创建字典数据"""
    pass

class DictDataUpdate(BaseModel):
    """更新字典数据"""
    dict_label: Optional[str] = Field(None, max_length=100, description="字典标签")
    dict_value: Optional[str] = Field(None, max_length=100, description="字典值")
    parent_code: Optional[str] = Field(None, max_length=50, description="父编码")
    sort_order: Optional[int] = Field(None, description="排序")
    css_class: Optional[str] = Field(None, max_length=50, description="CSS类名")
    is_default: Optional[bool] = Field(None, description="是否默认")
    is_active: Optional[bool] = Field(None, description="是否启用")
    remark: Optional[str] = Field(None, description="备注")
    extra_data: Optional[DictExtraData] = Field(None, description="扩展数据")
    
    @field_validator('extra_data', mode='before')
    @classmethod
    def parse_extra_data(cls, v: Any) -> Optional[DictExtraData]:
        """解析JSON字符串为DictExtraData"""
        if isinstance(v, str):
            data = json.loads(v) if v else None
            return DictExtraData(**data) if data else None
        if isinstance(v, dict):
            return DictExtraData(**v)
        if v is None:
            return None
        return None  # 其他类型返回 None

    model_config = ConfigDict(from_attributes=True)

class DictDataResponse(DictDataBase):
    """字典数据响应"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    