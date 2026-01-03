"""
分页响应 Schemas
统一的分页模型定义
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, TypeVar, List

# 泛型类型变量
T = TypeVar('T')


class PaginationInfo(BaseModel):
    """分页信息"""
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, le=1000, description="每页数量")
    total_pages: int = Field(..., ge=0, description="总页数")
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def create(cls, total: int, page: int, page_size: int) -> "PaginationInfo":
        """创建分页信息"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应（统一标准）
    
    使用示例：
    ```python
    @router.get("", response_model=PaginatedResponse[PersonResponse])
    def list_items(...) -> PaginatedResponse[PersonResponse]:
        return PaginatedResponse(
            data=items,
            total=total,
            page=page,
            page_size=page_size
        )
    ```
    """
    data: List[T] = Field(..., description="数据列表")
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, le=1000, description="每页数量")
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def total_pages(self) -> int:
        """总页数"""
        return (self.total + self.page_size - 1) // self.page_size if self.page_size > 0 else 0
    
    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1
