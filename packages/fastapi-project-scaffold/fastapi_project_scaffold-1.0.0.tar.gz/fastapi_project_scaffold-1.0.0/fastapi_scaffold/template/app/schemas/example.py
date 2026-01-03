from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ExampleBase(BaseModel):
    title: str
    content: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ExampleCreate(ExampleBase):
    pass

class ExampleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ExampleResponse(ExampleBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
