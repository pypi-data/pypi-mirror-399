from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    role_id: int
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserAdminResponse(BaseModel):
    id: int
    username: str
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    is_active: bool
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
