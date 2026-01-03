from functools import wraps
from typing import Callable, Any, Optional
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.operation_log import OperationLog
from app.models.user import User


def log_operation(action: str, resource: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    操作日志装饰器
    
    Args:
        action: 操作类型 (create/update/delete/read)
        resource: 资源名称 (users/roles/examples等)
        
    Usage:
        @router.delete("/api/users/{user_id}")
        @log_operation("delete", "users")
        def delete_user(user_id: int, ...):
            pass
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)
            
            try:
                current_user: Optional[User] = kwargs.get('current_user')
                db: Optional[Session] = kwargs.get('db')
                request: Optional[Request] = kwargs.get('request')
                
                if current_user and db:
                    resource_id: Optional[int] = None
                    for key in ['user_id', 'role_id', 'permission_id', 'example_id', 'id']:
                        if key in kwargs:
                            resource_id = kwargs[key]
                            break
                    
                    ip_address = "unknown"
                    if request:
                        ip_address = request.client.host if request.client else "unknown"
                    
                    log = OperationLog(
                        user_id=current_user.id,
                        username=current_user.username,
                        action=action,
                        resource=resource,
                        resource_id=resource_id,
                        ip_address=ip_address
                    )
                    db.add(log)
                    db.commit()
            except Exception as e:
                print(f"Failed to log operation: {e}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            
            try:
                current_user: Optional[User] = kwargs.get('current_user')
                db: Optional[Session] = kwargs.get('db')
                request: Optional[Request] = kwargs.get('request')
                
                if current_user and db:
                    resource_id: Optional[int] = None
                    for key in ['user_id', 'role_id', 'permission_id', 'example_id', 'id']:
                        if key in kwargs:
                            resource_id = kwargs[key]
                            break
                    
                    ip_address = "unknown"
                    if request:
                        ip_address = request.client.host if request.client else "unknown"
                    
                    log = OperationLog(
                        user_id=current_user.id,
                        username=current_user.username,
                        action=action,
                        resource=resource,
                        resource_id=resource_id,
                        ip_address=ip_address
                    )
                    db.add(log)
                    db.commit()
            except Exception as e:
                print(f"Failed to log operation: {e}")
            
            return result
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
