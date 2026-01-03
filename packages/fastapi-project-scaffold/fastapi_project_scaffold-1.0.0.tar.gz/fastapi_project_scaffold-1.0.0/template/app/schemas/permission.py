from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class PermissionBase(BaseModel):
    resource: str
    action: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PermissionResponse(PermissionBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
