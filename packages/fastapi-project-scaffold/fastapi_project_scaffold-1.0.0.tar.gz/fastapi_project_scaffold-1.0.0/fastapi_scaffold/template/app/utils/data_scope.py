from sqlalchemy.orm import Query
from app.models.user import User


def apply_data_filter(query: Query, user: User, model) -> Query:
    """
    应用数据权限过滤
    
    普通用户只能查看/编辑自己创建的数据
    管理员和超级管理员可以查看所有数据
    
    Args:
        query: SQLAlchemy 查询对象
        user: 当前用户
        model: 数据模型类
        
    Returns:
        过滤后的查询对象
    """
    # 管理员和超级管理员可以查看所有数据
    if user.role and user.role.name in ['admin', 'super_admin']:
        return query
    
    # 普通用户只能查看自己创建的数据
    if hasattr(model, 'created_by'):
        query = query.filter(model.created_by == user.id)
    
    return query
