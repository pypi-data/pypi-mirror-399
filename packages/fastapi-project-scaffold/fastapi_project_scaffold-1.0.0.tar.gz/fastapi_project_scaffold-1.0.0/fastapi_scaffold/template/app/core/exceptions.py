"""
统一异常和错误码定义
"""
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, Field


# ========== 错误码枚举 ==========

class ErrorCode(str, Enum):
    """错误码枚举（所有错误码定义）"""
    
    # ===== 设备相关错误 (DEVICE_*) =====
    DEVICE_NOT_FOUND = "DEVICE_NOT_FOUND"                    # 设备不存在
    DEVICE_ALREADY_EXISTS = "DEVICE_ALREADY_EXISTS"          # 设备已存在
    DEVICE_DISABLED = "DEVICE_DISABLED"                      # 设备已禁用
    DEVICE_OFFLINE = "DEVICE_OFFLINE"                        # 设备离线
    DEVICE_CONFLICT = "DEVICE_CONFLICT"                      # 设备冲突（重复序列号等）
    
    # Token相关
    DEVICE_TOKEN_MISSING = "DEVICE_TOKEN_MISSING"            # 缺少Token
    DEVICE_TOKEN_INVALID = "DEVICE_TOKEN_INVALID"            # Token无效
    DEVICE_TOKEN_EXPIRED = "DEVICE_TOKEN_EXPIRED"            # Token过期
    DEVICE_TOKEN_MALFORMED = "DEVICE_TOKEN_MALFORMED"        # Token格式错误
    
    # 设备状态相关
    DEVICE_NOT_REGISTERED = "DEVICE_NOT_REGISTERED"          # 设备未注册
    DEVICE_PENDING_APPROVAL = "DEVICE_PENDING_APPROVAL"      # 等待审批
    DEVICE_REJECTED = "DEVICE_REJECTED"                      # 设备已被拒绝
    DEVICE_INVALID_STATE = "DEVICE_INVALID_STATE"            # 设备状态不允许该操作
    DEVICE_NOT_IDLE = "DEVICE_NOT_IDLE"                      # 设备不是 idle 状态
    DEVICE_NOT_ACTIVE = "DEVICE_NOT_ACTIVE"                  # 设备不是 active 状态
    
    # 工位相关
    STATION_NOT_ASSIGNED = "STATION_NOT_ASSIGNED"            # 未分配工位
    STATION_NOT_FOUND = "STATION_NOT_FOUND"                  # 工位不存在
    STATION_OCCUPIED = "STATION_OCCUPIED"                    # 工位已被占用
    STATION_DISABLED = "STATION_DISABLED"                    # 工位已禁用
    
    # ===== 通用错误 (COMMON_*) =====
    VALIDATION_ERROR = "VALIDATION_ERROR"                    # 数据验证错误
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"                # 资源不存在
    PERMISSION_DENIED = "PERMISSION_DENIED"                  # 权限不足
    UNAUTHORIZED = "UNAUTHORIZED"                            # 未认证
    BAD_REQUEST = "BAD_REQUEST"                              # 错误的请求
    INTERNAL_ERROR = "INTERNAL_ERROR"                        # 内部错误
    
    # ===== 业务错误 (BUSINESS_*) =====
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"                      # 重复条目
    INVALID_OPERATION = "INVALID_OPERATION"                  # 无效操作
    OPERATION_FORBIDDEN = "OPERATION_FORBIDDEN"              # 操作被禁止


# ========== 统一错误响应格式 ==========

class ErrorResponse(BaseModel):
    """统一错误响应格式"""
    error_code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="时间戳（ISO格式）")
    details: Optional[Dict[str, Any]] = Field(default=None, description="详细信息")
    
    model_config = {"json_schema_extra": {
        "example": {
            "error_code": "DEVICE_NOT_FOUND",
            "message": "设备ID 166不存在",
            "timestamp": "2025-12-26T12:00:00Z",
            "details": {
                "device_id": 166,
                "last_seen": "2025-12-25T10:30:00Z"
            }
        }
    }}


# ========== 自定义异常类 ==========

class AppException(HTTPException):
    """应用异常基类（携带错误码）"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.error_message = message
        self.details = details or {}
        
        # 构造错误响应
        error_response = ErrorResponse(
            error_code=error_code.value,
            message=message,
            details=details
        )
        
        # 添加错误码到headers（便于客户端快速解析）
        headers = {"X-Error-Code": error_code.value}
        
        super().__init__(
            status_code=status_code,
            detail=error_response.model_dump(),
            headers=headers
        )


# ========== 设备相关异常 ==========

class DeviceNotFoundException(AppException):
    """设备不存在"""
    def __init__(self, device_id: int, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.DEVICE_NOT_FOUND,
            message=f"设备ID {device_id}不存在",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details or {"device_id": device_id}
        )


class DeviceTokenInvalidException(AppException):
    """Token无效"""
    def __init__(self, message: str = "设备Token无效", details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.DEVICE_TOKEN_INVALID,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class DeviceTokenExpiredException(AppException):
    """Token已过期"""
    def __init__(self, expired_at: datetime, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.DEVICE_TOKEN_EXPIRED,
            message="设备Token已过期",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details or {"expired_at": expired_at.isoformat()}
        )


class DeviceTokenMissingException(AppException):
    """缺少Token"""
    def __init__(self, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.DEVICE_TOKEN_MISSING,
            message="缺少设备Token（Authorization: Bearer <device_token>）",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class DeviceDisabledException(AppException):
    """设备已禁用"""
    def __init__(self, device_id: int, reason: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.DEVICE_DISABLED,
            message="设备已被管理员禁用",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details or {
                "device_id": device_id,
                "reason": reason or "未提供禁用原因"
            }
        )


class DeviceConflictException(AppException):
    """设备冲突（如：重复序列号）"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.DEVICE_CONFLICT,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


# ========== 工位相关异常 ==========

class StationNotFoundException(AppException):
    """工位不存在"""
    def __init__(self, station_id: int, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.STATION_NOT_FOUND,
            message=f"工位ID {station_id}不存在",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details or {"station_id": station_id}
        )


class StationOccupiedException(AppException):
    """工位已被占用"""
    def __init__(self, station_id: int, occupying_device: str, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.STATION_OCCUPIED,
            message=f"工位已被设备 {occupying_device} 占用",
            status_code=status.HTTP_409_CONFLICT,
            details=details or {
                "station_id": station_id,
                "occupying_device": occupying_device
            }
        )


class StationDisabledException(AppException):
    """工位已禁用"""
    def __init__(self, station_id: int, details: Optional[Dict] = None):
        super().__init__(
            error_code=ErrorCode.STATION_DISABLED,
            message=f"工位ID {station_id}已被禁用",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details or {"station_id": station_id}
        )


# ========== 便捷函数 ==========

def raise_device_not_found(device_id: int, details: Optional[Dict] = None) -> None:
    """抛出设备不存在异常"""
    raise DeviceNotFoundException(device_id=device_id, details=details)


def raise_device_token_invalid(message: str = "设备Token无效", details: Optional[Dict] = None) -> None:
    """抛出Token无效异常"""
    raise DeviceTokenInvalidException(message=message, details=details)


def raise_device_token_expired(expired_at: datetime, details: Optional[Dict] = None) -> None:
    """抛出Token过期异常"""
    raise DeviceTokenExpiredException(expired_at=expired_at, details=details)


def raise_device_token_missing(details: Optional[Dict] = None) -> None:
    """抛出Token缺失异常"""
    raise DeviceTokenMissingException(details=details)


def raise_device_disabled(device_id: int, reason: Optional[str] = None, details: Optional[Dict] = None) -> None:
    """抛出设备已禁用异常"""
    raise DeviceDisabledException(device_id=device_id, reason=reason, details=details)


def raise_station_not_found(station_id: int, details: Optional[Dict] = None) -> None:
    """抛出工位不存在异常"""
    raise StationNotFoundException(station_id=station_id, details=details)


def raise_station_occupied(station_id: int, occupying_device: str, details: Optional[Dict] = None) -> None:
    """抛出工位已占用异常"""
    raise StationOccupiedException(station_id=station_id, occupying_device=occupying_device, details=details)


def raise_station_disabled(station_id: int, details: Optional[Dict] = None) -> None:
    """抛出工位已禁用异常"""
    raise StationDisabledException(station_id=station_id, details=details)
