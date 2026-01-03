"""
字典管理 CRUD 操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from app.models.dict import DictType, DictData


class DictTypeCRUD:
    """字典类型 CRUD"""
    
    def get_by_code(self, db: Session, type_code: str) -> Optional[DictType]:
        """根据类型编码获取"""
        return db.query(DictType).filter(DictType.type_code == type_code).first()
    
    def get_all(self, db: Session, is_active: Optional[bool] = None) -> List[DictType]:
        """获取所有类型"""
        query = db.query(DictType)
        if is_active is not None:
            query = query.filter(DictType.is_active == is_active)
        return query.order_by(DictType.id).all()
    
    def create(self, db: Session, obj_in: dict) -> DictType:
        """创建"""
        db_obj = DictType(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: DictType, obj_in: dict) -> DictType:
        """更新"""
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, db_obj: DictType) -> None:
        """删除"""
        db.delete(db_obj)
        db.commit()


class DictDataCRUD:
    """字典数据 CRUD"""
    
    def get_by_type(
        self, 
        db: Session, 
        type_code: str, 
        is_active: Optional[bool] = True,
        parent_code: Optional[str] = None
    ) -> List[DictData]:
        """获取指定类型的所有数据
        
        Args:
            type_code: 字典类型编码
            is_active: 是否启用
            parent_code: 父级编码过滤
                - None: 不过滤（返回所有）
                - "": 空字符串表示获取顶级（parent_code IS NULL）
                - "xxx": 获取指定父级下的子级
        """
        query = db.query(DictData).filter(DictData.type_code == type_code)
        if is_active is not None:
            query = query.filter(DictData.is_active == is_active)
        # parent_code 过滤
        if parent_code is not None:
            if parent_code == "" or parent_code == "null":
                # 空字符串或 "null" 表示获取顶级
                query = query.filter(DictData.parent_code.is_(None))
            else:
                # 获取指定父级下的子级
                query = query.filter(DictData.parent_code == parent_code)
        return query.order_by(DictData.sort_order, DictData.id).all()
    
    def get_by_code(
        self, 
        db: Session, 
        type_code: str, 
        dict_code: str
    ) -> Optional[DictData]:
        """根据类型和编码获取"""
        return db.query(DictData).filter(
            DictData.type_code == type_code,
            DictData.dict_code == dict_code
        ).first()
    
    def get(self, db: Session, id: int) -> Optional[DictData]:
        """根据ID获取"""
        return db.query(DictData).filter(DictData.id == id).first()
    
    def get_all_grouped(
        self, 
        db: Session, 
        is_active: Optional[bool] = True
    ) -> Dict[str, List[DictData]]:
        """获取所有数据，按类型分组"""
        query = db.query(DictData)
        if is_active is not None:
            query = query.filter(DictData.is_active == is_active)
        all_data = query.order_by(
            DictData.type_code, 
            DictData.sort_order, 
            DictData.id
        ).all()
        
        # 按类型分组
        grouped: Dict[str, List[DictData]] = {}
        for item in all_data:
            if item.type_code not in grouped:
                grouped[item.type_code] = []
            grouped[item.type_code].append(item)
        
        return grouped
    
    def create(self, db: Session, obj_in: dict) -> DictData:
        """创建"""
        db_obj = DictData(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: DictData, obj_in: dict) -> DictData:
        """更新"""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, db_obj: DictData) -> None:
        """删除"""
        db.delete(db_obj)
        db.commit()


# 实例化
dict_type_crud = DictTypeCRUD()
dict_data_crud = DictDataCRUD()
