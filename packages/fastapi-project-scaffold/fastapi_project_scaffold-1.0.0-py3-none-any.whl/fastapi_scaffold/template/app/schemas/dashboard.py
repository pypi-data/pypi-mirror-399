"""Dashboard schemas - 仪表盘统计数据响应"""
from pydantic import BaseModel, ConfigDict, Field

class DashboardStatsResponse(BaseModel):
    """仪表盘统计数据响应"""
    
    # 人员统计
    person_count: int = Field(..., ge=0, description="人员总数")
    person_trend: str = Field(..., max_length=20, description="人员趋势（相对上周）")
    
    # 任务统计
    task_count: int = Field(..., ge=0, description="训练任务数")
    task_trend: str = Field(..., max_length=20, description="任务趋势（相对上周）")
    
    # 设备统计
    device_online: int = Field(..., ge=0, description="设备在线数")
    device_trend: str = Field(..., max_length=20, description="设备趋势（相对上周）")
    
    # 训练统计
    today_training: int = Field(..., ge=0, description="今日训练数")
    training_trend: str = Field(..., max_length=20, description="训练趋势（相对昨日）")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "person_count": 156,
                "person_trend": "+12%",
                "task_count": 42,
                "task_trend": "+8%",
                "device_online": 28,
                "device_trend": "+3%",
                "today_training": 15,
                "training_trend": "+25%"
            }
        }
    )
