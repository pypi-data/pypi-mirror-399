"""
设备管理工具函数
"""
import secrets
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.device import Device
from app.core.exceptions import (
    raise_device_not_found,
    raise_device_token_invalid,
    raise_device_token_expired,
    raise_device_disabled
)


def generate_device_code(db: Session, device_type: str) -> str:
    """
    生成设备编号
    
    Args:
        db: 数据库会话
        device_type: 设备类型 (vr/pad/wristband)
    
    Returns:
        设备编号 (如: VR-001, PAD-002, BAND-003)
    """
    # 前缀映射
    prefix_map = {
        'vr': 'VR',
        'pad': 'PAD',
        'wristband': 'BAND'
    }
    
    prefix = prefix_map.get(device_type, 'DEV')
    
    # 查询该类型设备的最大编号
    max_code = db.query(func.max(Device.device_code)).filter(
        Device.device_type == device_type
    ).scalar()
    
    if not max_code:
        return f"{prefix}-001"
    
    # 提取数字部分
    try:
        number = int(max_code.split('-')[1])
        return f"{prefix}-{number + 1:03d}"
    except (IndexError, ValueError):
        # 如果解析失败，查询该类型设备总数+1
        count = db.query(Device).filter(Device.device_type == device_type).count()
        return f"{prefix}-{count + 1:03d}"


def generate_device_token() -> str:
    """
    生成设备Token（256位随机字符串）
    
    Returns:
        Token字符串
    """
    return secrets.token_urlsafe(32)


def verify_device_token(db: Session, device_id: int, token: str) -> Device:
    """
    验证设备Token
    
    Args:
        db: 数据库会话
        device_id: 设备ID
        token: 设备Token
    
    Returns:
        设备对象（验证成功）
    
    Raises:
        DeviceNotFoundException: 设备不存在
        DeviceTokenInvalidException: Token无效
        DeviceTokenExpiredException: Token过期
        DeviceDisabledException: 设备已禁用
    """
    # 查询设备
    device: Optional[Device] = db.query(Device).filter(Device.id == device_id).first()
    
    if device is None:
        raise_device_not_found(device_id)
    
    # mypy类型收窄：此后device不为None
    assert device is not None
    
    # 验证Token
    if device.device_token != token:
        raise_device_token_invalid(
            message="设备Token无效",
            details={"device_id": device_id}
        )
    
    # 检查Token是否过期（token_expires_at为NULL表示永久有效）
    if device.token_expires_at is not None:
        if datetime.utcnow() > device.token_expires_at:
            raise_device_token_expired(
                expired_at=device.token_expires_at,
                details={"device_id": device_id}
            )
    
    # 检查设备状态
    if device.status == 'disabled':
        raise_device_disabled(
            device_id=device_id,
            reason=device.reject_reason,
            details={"status": device.status}
        )
    
    return device


def extract_device_token_from_header(x_device_token: Optional[str]) -> Optional[str]:
    """
    从 X-Device-Token header 中提取 Token
    
    Args:
        x_device_token: X-Device-Token header 值
    
    Returns:
        Token 字符串或 None
    
    注意: 已从 Authorization: Bearer <token> 迁移到 X-Device-Token: <token>
    """
    # 直接返回，不需要解析 Bearer 前缀
    return x_device_token if x_device_token else None
