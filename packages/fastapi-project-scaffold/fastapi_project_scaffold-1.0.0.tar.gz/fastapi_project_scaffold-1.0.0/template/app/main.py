from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)
from app.database import engine, Base
from app.api import auth, profile, users, roles, permissions, examples, enums, dict as dict_api, dashboard

# 导入所有模型以确保SQLAlchemy正确注册
from app.models import Role, Permission, User, Example, RefreshToken, OperationLog, role_permissions
from app.models.dict import DictType, DictData
from app.models.system_config import SystemConfig

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI-RBAC-Scaffold",
    description="企业级 FastAPI 脚手架 with JWT + RBAC 权限管理",
    version="1.0.0"
)

# 422 验证错误处理器（详细日志）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """捕获 422 验证错误并打印详细日志"""
    logger.error("="*60)
    logger.error("❌ 422 验证错误")
    logger.error("="*60)
    logger.error(f"请求路径: {request.url.path}")
    logger.error(f"请求方法: {request.method}")
    
    # 打印原始请求体
    try:
        body = await request.body()
        logger.error(f"原始请求体: {body!r}")
        logger.error(f"解码后: {body.decode('utf-8')}")
    except Exception as e:
        logger.error(f"读取请求体失败: {e}")
    
    # 打印验证错误详情
    logger.error(f"验证错误详情:")
    for error in exc.errors():
        logger.error(f"  - 位置: {error.get('loc')}")
        logger.error(f"    类型: {error.get('type')}")
        logger.error(f"    消息: {error.get('msg')}")
        logger.error(f"    输入: {error.get('input')}")
    
    logger.error("="*60)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（基础模块）
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(examples.router)
app.include_router(enums.router)
app.include_router(dict_api.router)
app.include_router(dashboard.router)

# TODO: 在此处注册业务模块路由
# 示例:
# from app.api.v1 import articles
# app.include_router(articles.router, prefix="/api/v1/articles", tags=["文章管理"])


@app.get("/")
def root():
    return {
        "message": "FastAPI-RBAC-Scaffold API",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "企业级 FastAPI 脚手架，开箱即用的 JWT + RBAC 权限管理"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
