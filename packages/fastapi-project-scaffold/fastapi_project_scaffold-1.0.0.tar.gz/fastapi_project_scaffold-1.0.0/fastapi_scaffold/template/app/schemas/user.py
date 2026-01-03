from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    password: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    model_config = ConfigDict(from_attributes=True)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class NextAction(str, Enum):
    """设备登录后的下一步操作"""
    TRAINING_TASKS = "training_tasks"      # 跳转到训练任务列表
    WAITING_STATION = "waiting_station"    # 等待分配工位
    WELCOME = "welcome"                    # 欢迎页面（首次登录）
    PROFILE_SETUP = "profile_setup"        # 完善个人信息

class StationInfo(BaseModel):
    """工位详细信息"""
    station_id: int
    station_code: str
    station_name: str
    station_status: str  # idle, occupied, maintenance
    
    model_config = ConfigDict(from_attributes=True)

class DeviceInfo(BaseModel):
    """设备信息（增强）"""
    device_id: int
    device_code: str
    device_name: str
    device_type: str
    station_id: Optional[int] = None
    device_status: str  # registered, idle, active, disabled
    
    model_config = ConfigDict(from_attributes=True)

class DeviceTokenResponse(TokenResponse):
    """设备端登录响应（增强）"""
    device_info: DeviceInfo
    station_info: Optional[StationInfo] = None  # 工位信息（如果已分配）
    next_action: NextAction  # 下一步操作
    can_start_training: bool  # 是否可以开始训练
    is_first_login: bool = False  # 是否首次登录
    waiting_reason: Optional[str] = None  # 等待原因（如果需要等待）
    message: str = "登录成功"  # 提示消息
