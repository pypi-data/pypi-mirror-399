from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RoleResponse(RoleBase):
    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class RoleWithPermissions(RoleResponse):
    permission_ids: List[int] = []

class RolePermissionUpdate(BaseModel):
    permission_ids: List[int]
    
    model_config = ConfigDict(from_attributes=True)
