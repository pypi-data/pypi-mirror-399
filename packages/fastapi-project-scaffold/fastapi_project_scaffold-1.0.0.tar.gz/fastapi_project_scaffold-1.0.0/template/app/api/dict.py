"""
字典管理 API
提供字典类型和字典数据的CRUD接口
"""
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Body, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from io import BytesIO, StringIO
import csv

from app.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.dict import DictType, DictData
from app.schemas.dict import (
    DictTypeCreate,
    DictTypeUpdate,
    DictTypeResponse,
    DictDataCreate,
    DictDataUpdate,
    DictDataResponse
)
from app.schemas.common import MessageResponse, ReferenceCheckResponse
from app.schemas.common import BatchOperationResult, ImportResult
from app.crud.dict import dict_type_crud, dict_data_crud

# 尝试导入 pandas（可选依赖）
try:
    import pandas as pd  # type: ignore[import-untyped]
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

router = APIRouter(prefix="/api/dict", tags=["Dictionary"])


# ==================== 字典类型接口 ====================

@router.get("/types", response_model=List[DictTypeResponse])
def get_dict_types(
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[DictTypeResponse]:
    """获取所有字典类型"""
    types = dict_type_crud.get_all(db, is_active)
    return [DictTypeResponse.model_validate(t) for t in types]


@router.get("/types/{type_code}", response_model=DictTypeResponse)
def get_dict_type(
    type_code: str = Path(..., description="字典类型编码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DictTypeResponse:
    """获取指定字典类型详情"""
    dict_type = dict_type_crud.get_by_code(db, type_code)
    if not dict_type:
        raise HTTPException(status_code=404, detail=f"字典类型 {type_code} 不存在")
    return DictTypeResponse.model_validate(dict_type)


@router.post("/types", response_model=DictTypeResponse)
def create_dict_type(
    data: DictTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DictTypeResponse:
    """创建字典类型"""
    # 检查类型编码是否已存在
    existing = dict_type_crud.get_by_code(db, data.type_code)
    if existing:
        raise HTTPException(status_code=400, detail=f"类型编码 {data.type_code} 已存在")
    
    # 创建
    obj_dict = data.model_dump()
    obj_dict["created_by"] = current_user.id
    obj_dict["updated_by"] = current_user.id
    
    dict_type = dict_type_crud.create(db, obj_dict)
    return DictTypeResponse.model_validate(dict_type)


@router.put("/types/{id}", response_model=DictTypeResponse)
def update_dict_type(
    id: int = Path(..., description="字典类型ID"),
    data: DictTypeUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DictTypeResponse:
    """更新字典类型"""
    dict_type = db.query(DictType).filter(DictType.id == id).first()
    if not dict_type:
        raise HTTPException(status_code=404, detail=f"字典类型 {id} 不存在")
    
    # 更新
    obj_dict = data.model_dump(exclude_unset=True)
    obj_dict["updated_by"] = current_user.id
    
    updated = dict_type_crud.update(db, dict_type, obj_dict)
    return DictTypeResponse.model_validate(updated)


@router.delete("/types/{id}", response_model=MessageResponse)
def delete_dict_type(
    id: int = Path(..., description="字典类型ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MessageResponse:
    """删除字典类型"""
    dict_type = db.query(DictType).filter(DictType.id == id).first()
    if not dict_type:
        raise HTTPException(status_code=404, detail=f"字典类型 {id} 不存在")
    
    # 检查是否有关联的字典数据
    data_list = dict_data_crud.get_by_type(db, dict_type.type_code, is_active=None)
    if data_list:
        raise HTTPException(
            status_code=400,
            detail=f"该字典类型下有 {len(data_list)} 条数据，请先删除数据"
        )
    
    dict_type_crud.delete(db, dict_type)
    return MessageResponse(message="删除成功")


# ==================== 字典数据接口 ====================

@router.get("/data/{type_code}", response_model=List[DictDataResponse])
def get_dict_data_by_type(
    type_code: str = Path(..., description="字典类型编码"),
    is_active: Optional[bool] = Query(True, description="是否启用"),
    parent_code: Optional[str] = Query(None, description="父级编码过滤（空字符串或'null'表示获取顶级）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[DictDataResponse]:
    """获取指定类型的字典数据
    
    支持 parent_code 参数进行层级过滤：
    - 不传：返回所有数据
    - 空字符串或'null'：返回顶级数据（parent_code IS NULL）
    - 具体值：返回该父级下的子级数据
    """
    data = dict_data_crud.get_by_type(db, type_code, is_active, parent_code)
    return [DictDataResponse.model_validate(d) for d in data]


@router.get("/all", response_model=dict[str, list[DictDataResponse]])
def get_all_dict_data(
    is_active: Optional[bool] = Query(True, description="是否启用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict[str, list[DictDataResponse]]:
    """获取所有字典数据（按类型分组）
    返回格式：{ "dept": [...], "position": [...], ... }
    """
    grouped_data = dict_data_crud.get_all_grouped(db, is_active)
    
    # 转换为响应格式
    result: dict[str, list[DictDataResponse]] = {}
    for type_code, items in grouped_data.items():
        result[type_code] = [DictDataResponse.model_validate(item) for item in items]
    
    return result


@router.get("/data/detail/{id}", response_model=DictDataResponse)
def get_dict_data_detail(
    id: int = Path(..., description="字典数据ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DictDataResponse:
    """获取字典数据详情"""
    dict_data = dict_data_crud.get(db, id)
    if not dict_data:
        raise HTTPException(status_code=404, detail=f"字典数据 {id} 不存在")
    return DictDataResponse.model_validate(dict_data)


@router.post("/data", response_model=DictDataResponse)
def create_dict_data(
    data: DictDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DictDataResponse:
    """创建字典数据"""
    # 检查类型是否存在
    dict_type = dict_type_crud.get_by_code(db, data.type_code)
    if not dict_type:
        raise HTTPException(status_code=404, detail=f"字典类型 {data.type_code} 不存在")
    
    # 检查编码是否已存在
    existing = dict_data_crud.get_by_code(db, data.type_code, data.dict_code)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"字典编码 {data.dict_code} 在类型 {data.type_code} 下已存在"
        )
    
    # 创建
    obj_dict = data.model_dump()
    obj_dict["created_by"] = current_user.id
    obj_dict["updated_by"] = current_user.id
    
    dict_data = dict_data_crud.create(db, obj_dict)
    return DictDataResponse.model_validate(dict_data)


@router.put("/data/{id}", response_model=DictDataResponse)
def update_dict_data(
    id: int = Path(..., description="字典数据ID"),
    data: DictDataUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DictDataResponse:
    """更新字典数据"""
    dict_data = dict_data_crud.get(db, id)
    if not dict_data:
        raise HTTPException(status_code=404, detail=f"字典数据 {id} 不存在")
    
    # 更新
    obj_dict = data.model_dump(exclude_unset=True)
    obj_dict["updated_by"] = current_user.id
    
    updated = dict_data_crud.update(db, dict_data, obj_dict)
    return DictDataResponse.model_validate(updated)


@router.delete("/data/{id}", response_model=MessageResponse)
def delete_dict_data(
    id: int = Path(..., description="字典数据ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> MessageResponse:
    """删除字典数据"""
    dict_data = dict_data_crud.get(db, id)
    if not dict_data:
        raise HTTPException(status_code=404, detail=f"字典数据 {id} 不存在")
    
    # 检查删除权限
    dict_type = dict_type_crud.get_by_code(db, dict_data.type_code)
    if dict_type and not dict_type.allow_delete:
        raise HTTPException(status_code=403, detail="此字典类型不允许删除数据")
    
    dict_data_crud.delete(db, dict_data)
    return MessageResponse(message="删除成功")


@router.get("/data/{id}/references", response_model=ReferenceCheckResponse)
def check_dict_data_references(
    id: int = Path(..., description="字典数据ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ReferenceCheckResponse:
    """检查字典数据引用情况"""
    dict_data = dict_data_crud.get(db, id)
    if not dict_data:
        raise HTTPException(status_code=404, detail=f"字典数据 {id} 不存在")
    
    # TODO: 根据实际业务表检查引用
    # references: List[ReferenceItem] = []
    
    return ReferenceCheckResponse(
        can_delete=True,
        references=[]
    )


@router.post("/data/batch/enable", response_model=BatchOperationResult)
def batch_enable_dict_data(
    ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BatchOperationResult:
    """批量启用字典数据"""
    success = 0
    errors = []
    
    for id in ids:
        try:
            dict_data = dict_data_crud.get(db, id)
            if not dict_data:
                errors.append(f"ID {id}: 不存在")
                continue
            dict_data_crud.update(db, dict_data, {"is_active": True, "updated_by": current_user.id})
            success += 1
        except Exception as e:
            errors.append(f"ID {id}: {str(e)}")
    
    return BatchOperationResult(
        success_count=success,
        failure_count=len(errors),
        total_count=len(ids),
        errors=errors if errors else None
    )


@router.post("/data/batch/disable", response_model=BatchOperationResult)
def batch_disable_dict_data(
    ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BatchOperationResult:
    """批量禁用字典数据"""
    success = 0
    errors = []
    
    for id in ids:
        try:
            dict_data = dict_data_crud.get(db, id)
            if not dict_data:
                errors.append(f"ID {id}: 不存在")
                continue
            dict_data_crud.update(db, dict_data, {"is_active": False, "updated_by": current_user.id})
            success += 1
        except Exception as e:
            errors.append(f"ID {id}: {str(e)}")
    
    return BatchOperationResult(
        success_count=success,
        failure_count=len(errors),
        total_count=len(ids),
        errors=errors if errors else None
    )


@router.post("/data/batch-delete", response_model=BatchOperationResult)
def batch_delete_dict_data(
    ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> BatchOperationResult:
    """批量删除字典数据"""
    success = 0
    errors = []
    
    for id in ids:
        try:
            dict_data = dict_data_crud.get(db, id)
            if not dict_data:
                errors.append(f"ID {id}: 不存在")
                continue
            
            # 检查删除权限
            dict_type = dict_type_crud.get_by_code(db, dict_data.type_code)
            if dict_type and not dict_type.allow_delete:
                errors.append(f"ID {id}: 字典数据 {dict_data.dict_label} 不允许删除")
                continue
            
            dict_data_crud.delete(db, dict_data)
            success += 1
        except Exception as e:
            errors.append(f"ID {id}: {str(e)}")
    
    return BatchOperationResult(
        success_count=success,
        failure_count=len(errors),
        total_count=len(ids),
        errors=errors if errors else None
    )


# ==================== 导入导出 ====================

@router.get("/template/{type_code}", response_model=None)
def download_template(
    type_code: str = Path(..., description="字典类型编码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StreamingResponse:
    """下载导入模板（CSV格式）"""
    # 检查类型是否存在
    dict_type = dict_type_crud.get_by_code(db, type_code)
    if not dict_type:
        raise HTTPException(status_code=404, detail=f"字典类型 {type_code} 不存在")
    
    # 创建 CSV 模板
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        '字典编码*',
        '字典标签*',
        '字典值*',
        '父级编码',
        '排序',
        'CSS类名',
        '是否默认',
        '是否启用',
        '备注'
    ])
    
    # 写入示例数据
    writer.writerow([
        'EXAMPLE',
        '示例数据',
        'example_value',
        '',
        '0',
        'primary',
        '否',
        '是',
        '这是示例，请删除后填入实际数据'
    ])
    
    # 转换为字节流
    output.seek(0)
    content = output.getvalue().encode('utf-8-sig')  # 使用 UTF-8 BOM 以支持 Excel
    
    return StreamingResponse(
        BytesIO(content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=dict_{type_code}_template.csv"
        }
    )


@router.post("/import/{type_code}", response_model=ImportResult)
async def import_dict_data(
    type_code: str = Path(..., description="字典类型编码"),
    file: UploadFile = File(..., description="CSV文件"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ImportResult:
    """导入字典数据（CSV格式）"""
    # 检查类型是否存在
    dict_type = dict_type_crud.get_by_code(db, type_code)
    if not dict_type:
        raise HTTPException(status_code=404, detail=f"字典类型 {type_code} 不存在")
    
    # 检查新增权限
    if not dict_type.allow_add:
        raise HTTPException(status_code=403, detail="此字典类型不允许新增数据")
    
    # 读取文件内容
    content = await file.read()
    
    try:
        # 解析 CSV
        csv_file = StringIO(content.decode('utf-8-sig'))
        reader = csv.DictReader(csv_file)
        
        success = 0
        failed = 0
        skipped = 0
        failed_items = []
        total = 0
        
        for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
            total += 1
            
            try:
                # 验证必填字段
                if not row.get('字典编码*') or not row.get('字典标签*') or not row.get('字典值*'):
                    skipped += 1
                    continue
                
                # 检查编码是否已存在
                dict_code = row['字典编码*'].strip()
                existing = dict_data_crud.get_by_code(db, type_code, dict_code)
                
                # 构建数据
                data = {
                    'type_code': type_code,
                    'dict_code': dict_code,
                    'dict_label': row['字典标签*'].strip(),
                    'dict_value': row['字典值*'].strip(),
                    'parent_code': row.get('父级编码', '').strip() or None,
                    'sort_order': int(row.get('排序', '0') or '0'),
                    'css_class': row.get('CSS类名', '').strip() or None,
                    'is_default': row.get('是否默认', '否').strip() == '是',
                    'is_active': row.get('是否启用', '是').strip() == '是',
                    'remark': row.get('备注', '').strip() or None,
                    'created_by': current_user.id,
                    'updated_by': current_user.id
                }
                
                if existing:
                    # 更新
                    dict_data_crud.update(db, existing, data)
                else:
                    # 创建
                    dict_data_crud.create(db, data)
                
                success += 1
                
            except Exception as e:
                failed += 1
                failed_items.append({
                    "row": row_num,
                    "dict_code": row.get('字典编码*', ''),
                    "error": str(e)
                })
        
        return ImportResult(
            success_count=success,
            failure_count=failed,
            total_count=total,
            skipped_count=skipped,
            failed_items=failed_items if failed_items else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败：{str(e)}")


@router.get("/export/{type_code}", response_model=None)
def export_dict_data(
    type_code: str = Path(..., description="字典类型编码"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StreamingResponse:
    """导出字典数据（CSV格式）"""
    # 检查类型是否存在
    dict_type = dict_type_crud.get_by_code(db, type_code)
    if not dict_type:
        raise HTTPException(status_code=404, detail=f"字典类型 {type_code} 不存在")
    
    # 获取数据
    data_list = dict_data_crud.get_by_type(db, type_code, is_active=None)
    
    # 创建 CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        '字典编码',
        '字典标签',
        '字典值',
        '父级编码',
        '排序',
        'CSS类名',
        '是否默认',
        '是否启用',
        '备注'
    ])
    
    # 写入数据
    for item in data_list:
        writer.writerow([
            item.dict_code,
            item.dict_label,
            item.dict_value,
            item.parent_code or '',
            item.sort_order,
            item.css_class or '',
            '是' if item.is_default else '否',
            '是' if item.is_active else '否',
            item.remark or ''
        ])
    
    # 转换为字节流
    output.seek(0)
    content = output.getvalue().encode('utf-8-sig')
    
    return StreamingResponse(
        BytesIO(content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=dict_{type_code}_export.csv"
        }
    )
