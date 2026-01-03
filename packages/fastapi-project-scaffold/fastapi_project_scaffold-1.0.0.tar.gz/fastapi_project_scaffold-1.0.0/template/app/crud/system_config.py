from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import json
import re
from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class CRUDSystemConfig:
    """系统配置 CRUD 操作类"""
    
    # ========== 基础 CRUD ==========
    
    def get(self, db: Session, id: int) -> Optional[SystemConfig]:
        """根据 ID 获取配置"""
        return db.query(SystemConfig).filter(SystemConfig.id == id).first()
    
    def get_by_key(self, db: Session, key: str) -> Optional[SystemConfig]:
        """根据配置键获取配置"""
        return db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    
    def get_list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        group: Optional[str] = None,
        is_public: Optional[bool] = None,
        order_by: str = "sort_order",
        order_dir: str = "asc"
    ) -> Tuple[List[SystemConfig], int]:
        """获取配置列表（支持分页、筛选、排序）"""
        query = db.query(SystemConfig)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    SystemConfig.config_key.contains(keyword),
                    SystemConfig.label.contains(keyword),
                    SystemConfig.description.contains(keyword)
                )
            )
        
        # 分组筛选
        if group:
            query = query.filter(SystemConfig.config_group == group)
        
        # 公开筛选
        if is_public is not None:
            query = query.filter(SystemConfig.is_public == is_public)
        
        # 排序
        order_column = getattr(SystemConfig, order_by, SystemConfig.sort_order)
        if order_dir == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # 统计和分页
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def create(self, db: Session, obj_in: SystemConfigCreate) -> SystemConfig:
        """创建配置"""
        # 验证
        self._validate_config_key(obj_in.config_key)
        self._validate_config_type(obj_in.config_type)
        self._validate_config_group(obj_in.config_group)
        if obj_in.config_value:
            self._validate_value_format(obj_in.config_type, obj_in.config_value)
        
        # 创建
        obj = SystemConfig(**obj_in.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(
        self,
        db: Session,
        obj: SystemConfig,
        obj_in: SystemConfigUpdate
    ) -> SystemConfig:
        """更新配置"""
        # 检查是否可编辑
        if not obj.is_editable:
            raise ValueError("该配置不可编辑")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 验证
        if "config_type" in update_data:
            self._validate_config_type(update_data["config_type"])
        if "config_group" in update_data:
            self._validate_config_group(update_data["config_group"])
        if "config_value" in update_data:
            config_type = update_data.get("config_type", obj.config_type)
            if update_data["config_value"]:
                self._validate_value_format(config_type, update_data["config_value"])
        
        # 更新
        for field, value in update_data.items():
            setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        return obj
    
    def update_value(
        self,
        db: Session,
        key: str,
        value: Optional[str]
    ) -> Optional[SystemConfig]:
        """仅更新配置值（快捷方法）"""
        obj = self.get_by_key(db, key)
        if not obj:
            return None
        
        if not obj.is_editable:
            raise ValueError("该配置不可编辑")
        
        # 验证值格式
        if value:
            self._validate_value_format(obj.config_type, value)
        
        obj.config_value = value
        db.commit()
        db.refresh(obj)
        return obj
    
    def delete(self, db: Session, id: int) -> bool:
        """删除配置"""
        obj = self.get(db, id)
        if not obj:
            return False
        
        if not obj.is_editable:
            raise ValueError("该配置不可删除")
        
        db.delete(obj)
        db.commit()
        return True
    
    def delete_by_key(self, db: Session, key: str) -> bool:
        """根据配置键删除"""
        obj = self.get_by_key(db, key)
        if not obj:
            return False
        
        if not obj.is_editable:
            raise ValueError("该配置不可删除")
        
        db.delete(obj)
        db.commit()
        return True
    
    # ========== 复杂查询 ==========
    
    def get_by_group(
        self,
        db: Session,
        group: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SystemConfig], int]:
        """根据分组获取配置列表"""
        query = db.query(SystemConfig).filter(
            SystemConfig.config_group == group
        ).order_by(SystemConfig.sort_order.asc())
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def get_public_configs(self, db: Session) -> Dict[str, Optional[str]]:
        """获取所有公开配置（字典格式）"""
        configs = db.query(SystemConfig).filter(
            SystemConfig.is_public == True
        ).all()
        
        return {config.config_key: config.config_value for config in configs}
    
    def get_public_configs_by_group(self, db: Session, group: str) -> Dict[str, Optional[str]]:
        """获取指定分组的公开配置（字典格式）"""
        configs = db.query(SystemConfig).filter(
            SystemConfig.is_public == True,
            SystemConfig.config_group == group
        ).all()
        
        return {config.config_key: config.config_value for config in configs}
    
    # ========== 批量操作 ==========
    
    def batch_update(
        self,
        db: Session,
        updates: Dict[str, Optional[str]]
    ) -> int:
        """批量更新配置值"""
        # 验证
        if not updates or not isinstance(updates, dict):
            raise ValueError("updates 必须是非空字典")
        
        if len(updates) > 50:
            raise ValueError("批量更新最多支持 50 个配置")
        
        updated_count = 0
        
        for key, value in updates.items():
            config = self.get_by_key(db, key)
            if not config:
                raise ValueError(f"配置不存在: {key}")
            
            if not config.is_editable:
                raise ValueError(f"配置不可编辑: {key}")
            
            # 验证值格式
            if value:
                self._validate_value_format(config.config_type, value)
            
            config.config_value = value
            updated_count += 1
        
        db.commit()
        return updated_count
    
    # ========== 验证方法 ==========
    
    def _validate_config_key(self, key: str):
        """验证配置键格式"""
        pattern = r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$"
        if not re.match(pattern, key):
            raise ValueError("配置键格式错误，应为: group.name (小写字母、数字、下划线)")
    
    def _validate_config_type(self, config_type: str):
        """验证配置类型"""
        allowed_types = ['string', 'number', 'boolean', 'json']
        if config_type not in allowed_types:
            raise ValueError(f"无效配置类型: {config_type}")
    
    def _validate_config_group(self, config_group: str):
        """验证配置分组"""
        allowed_groups = ['basic', 'appearance', 'business', 'advanced']
        if config_group not in allowed_groups:
            raise ValueError(f"无效配置分组: {config_group}")
    
    def _validate_value_format(self, config_type: str, value: str):
        """根据配置类型验证值格式"""
        if config_type == 'number':
            try:
                float(value)
            except ValueError:
                raise ValueError("配置值必须是数字格式")
        
        elif config_type == 'boolean':
            if value not in ['true', 'false', '1', '0']:
                raise ValueError("配置值必须是布尔格式 (true/false/1/0)")
        
        elif config_type == 'json':
            try:
                json.loads(value) if isinstance(value, str) else value
            except:
                raise ValueError("配置值必须是有效的 JSON 格式")


crud_system_config = CRUDSystemConfig()
