from typing import Any, Optional, cast
import casbin  # type: ignore[import-untyped]
from casbin_sqlalchemy_adapter import Adapter  # type: ignore[import-untyped]
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import engine
from app.models.role import Role
from app.models.permission import Permission

_enforcer: Optional[Any] = None


def get_enforcer() -> Any:  # type: ignore[misc]
    """获取Casbin执行器单例"""
    global _enforcer
    if _enforcer is None:
        model_path = Path(__file__).parent.parent.parent / "casbin" / "model.conf"
        adapter = Adapter(engine)
        _enforcer = casbin.Enforcer(str(model_path), adapter)  # type: ignore[attr-defined]
        _enforcer.load_policy()
    return _enforcer


def reload_policies() -> None:
    """重新加载策略（从数据库）"""
    enforcer = get_enforcer()
    enforcer.load_policy()


def sync_policies_from_db(db: Session) -> None:
    """从数据库同步权限策略到Casbin"""
    enforcer = get_enforcer()
    enforcer.clear_policy()
    
    roles = db.query(Role).all()
    for role in roles:
        for permission in role.permissions:
            enforcer.add_policy(role.name, permission.resource, permission.action)
    
    enforcer.save_policy()
    reload_policies()


def check_permission(user_role: str, resource: str, action: str) -> bool:
    """检查权限"""
    enforcer = get_enforcer()
    # Casbin enforcer.enforce returns bool, cast to ensure type safety
    return cast(bool, enforcer.enforce(user_role, resource, action))
