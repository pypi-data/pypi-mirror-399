"""Dashboard API - 仪表盘统计数据"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.schemas.dashboard import DashboardStatsResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DashboardStatsResponse:
    """
    获取仪表盘统计数据
    
    权限: 所有登录用户
    缓存: 建议 5 分钟
    
    Returns:
        DashboardStatsResponse: 包含用户、角色统计数据
    
    Note:
        这是一个示例实现，展示如何在脚手架中添加统计功能。
        在实际项目中，根据业务需求添加更多统计指标。
    """
    try:
        # 用户统计
        user_count = db.query(func.count(User.id)).filter(
            User.is_deleted == False
        ).scalar() or 0
        
        # 活跃用户统计
        active_user_count = db.query(func.count(User.id)).filter(
            User.is_deleted == False,
            User.is_active == True
        ).scalar() or 0
        
        return DashboardStatsResponse(
            person_count=user_count,
            person_trend="-",
            task_count=active_user_count,
            task_trend="-",
            device_online=0,
            device_trend="-",
            today_training=0,
            training_trend="-"
        )
    
    except Exception as e:
        # 降级策略：返回默认值
        return DashboardStatsResponse(
            person_count=0,
            person_trend="-",
            task_count=0,
            task_trend="-",
            device_online=0,
            device_trend="-",
            today_training=0,
            training_trend="-"
        )
