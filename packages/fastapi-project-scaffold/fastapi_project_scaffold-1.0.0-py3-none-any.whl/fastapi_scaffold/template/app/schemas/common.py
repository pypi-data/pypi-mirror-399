"""
通用响应 Schemas
用于非标准分页的列表响应、批量操作结果、导入结果等
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar('T')

# ==================== 通用消息响应 ====================

class MessageResponse(BaseModel):
    """消息响应（通用）"""
    message: str = Field(..., description="消息内容")
    
    model_config = ConfigDict(from_attributes=True)

class ReferenceItem(BaseModel):
    """引用项（用于检查是否可删除）"""
    table: str = Field(..., description="引用表名")
    count: int = Field(..., ge=0, description="引用数量")
    
    model_config = ConfigDict(from_attributes=True)

class ReferenceCheckResponse(BaseModel):
    """引用检查响应"""
    can_delete: bool = Field(..., description="是否可删除")
    references: List[ReferenceItem] = Field(default_factory=list, description="引用列表")
    
    model_config = ConfigDict(from_attributes=True)

# ==================== 列表响应 ====================

class ListResponse(BaseModel, Generic[T]):
    """
    简单列表响应（非分页，使用 skip/limit）
    
    用于 users, roles, permissions, examples 等使用 skip/limit 的端点
    
    使用示例：
    ```python
    @router.get("", response_model=ListResponse[RoleResponse])
    def list_roles(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
    ) -> ListResponse[RoleResponse]:
        total = db.query(Role).count()
        items = db.query(Role).offset(skip).limit(limit).all()
        return ListResponse(total=total, items=items)
    ```
    """
    total: int = Field(..., ge=0, description="总记录数")
    items: List[T] = Field(..., description="数据列表")
    
    model_config = ConfigDict(from_attributes=True)

class BatchOperationResult(BaseModel):
    """
    批量操作结果（统一标准）
    
    用于批量删除、批量审批、批量更新等操作
    
    使用示例：
    ```python
    @router.post("/batch-delete", response_model=BatchOperationResult)
    def batch_delete(ids: List[int], db: Session = Depends(get_db)) -> BatchOperationResult:
        success = 0
        errors = []
        
        for id in ids:
            try:
                crud.delete(db, id)
                success += 1
            except Exception as e:
                errors.append(f"ID {id}: {str(e)}")
        
        return BatchOperationResult(
            success_count=success,
            failure_count=len(errors),
            total_count=len(ids),
            errors=errors if errors else None
        )
    ```
    """
    success_count: int = Field(..., ge=0, description="成功数量")
    failure_count: int = Field(..., ge=0, description="失败数量")
    total_count: int = Field(..., ge=0, description="总数量")
    errors: Optional[List[str]] = Field(None, description="错误列表（可选）")
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def success_rate(self) -> float:
        """成功率（0.0 - 1.0）"""
        if self.total_count == 0:
            return 0.0
        return round(self.success_count / self.total_count, 4)

class ImportResult(BaseModel):
    """
    导入结果（统一标准）
    
    用于 Excel/CSV 导入人员、题目、配置等操作
    
    使用示例：
    ```python
    @router.post("/import", response_model=ImportResult)
    async def import_persons(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
    ) -> ImportResult:
        rows = parse_excel(file)
        
        success = failed = skipped = 0
        failed_items = []
        
        for idx, row in enumerate(rows, start=2):  # 从第2行开始（第1行是表头）
            # 验证格式
            if not validate(row):
                skipped += 1
                continue
            
            # 尝试导入
            try:
                create_person(db, row)
                success += 1
            except DuplicateError:
                failed += 1
                failed_items.append({
                    "row": idx,
                    "name": row.get('name'),
                    "error": "记录已存在"
                })
            except Exception as e:
                failed += 1
                failed_items.append({
                    "row": idx,
                    "data": row,
                    "error": str(e)
                })
        
        return ImportResult(
            success_count=success,
            failure_count=failed,
            total_count=len(rows),
            skipped_count=skipped,
            failed_items=failed_items if failed_items else None
        )
    ```
    """
    success_count: int = Field(..., ge=0, description="成功导入数量")
    failure_count: int = Field(..., ge=0, description="失败数量")
    total_count: int = Field(..., ge=0, description="总数量")
    skipped_count: int = Field(0, ge=0, description="跳过数量（格式错误、重复等）")
    failed_items: Optional[List[dict]] = Field(
        None, 
        description="失败项详情（包含行号、原始数据、错误原因）"
    )
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def success_rate(self) -> float:
        """成功率（0.0 - 1.0）"""
        if self.total_count == 0:
            return 0.0
        return round(self.success_count / self.total_count, 4)
