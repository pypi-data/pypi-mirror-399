# 最佳实践

**FastAPI Scaffold 开发最佳实践指南**

---

## 📋 目录

1. [项目组织](#1-项目组织)
2. [代码规范](#2-代码规范)
3. [数据库设计](#3-数据库设计)
4. [API 设计](#4-api-设计)
5. [认证和安全](#5-认证和安全)
6. [错误处理](#6-错误处理)
7. [性能优化](#7-性能优化)
8. [测试策略](#8-测试策略)
9. [部署建议](#9-部署建议)

---

## 1. 项目组织

### 1.1 目录结构

**✅ 推荐**:
```
app/
├── api/              # API 路由按功能分组
│   ├── auth.py      # 认证相关
│   ├── users.py     # 用户管理
│   └── v1/          # 版本化 API
│       ├── articles.py
│       └── comments.py
├── models/          # 每个模型一个文件
├── schemas/         # 每个实体一个文件
├── crud/            # CRUD 操作（可选）
└── core/            # 核心配置
```

**❌ 避免**:
```
app/
├── api.py           # 所有 API 在一个文件
├── models.py        # 所有模型在一个文件
└── schemas.py       # 所有 Schema 在一个文件
```

### 1.2 模块命名

**✅ 推荐**:
```python
# 单数名词，清晰语义
user.py
article.py
comment.py
order_item.py
```

**❌ 避免**:
```python
# 复数、缩写、动词
users.py          # 复数
art.py            # 缩写
create_user.py    # 动词
```

### 1.3 导入顺序

```python
# 1. 标准库
import os
from datetime import datetime

# 2. 第三方库
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. 本地导入
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
```

---

## 2. 代码规范

### 2.1 类型提示

**✅ 推荐**:
```python
from typing import Optional, List

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()
```

**❌ 避免**:
```python
def get_users(db, skip=0, limit=100):  # 无类型提示
    return db.query(User).offset(skip).limit(limit).all()
```

### 2.2 SQLAlchemy 2.0 风格

**✅ 推荐**:
```python
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(100))
```

**❌ 避免**:
```python
# SQLAlchemy 1.x 风格
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), nullable=True)
```

### 2.3 Pydantic 配置

**✅ 推荐**:
```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    
    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemy 2.0
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com"
            }
        }
    )
```

**❌ 避免**:
```python
# Pydantic 1.x 风格
class UserResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        orm_mode = True  # 旧版
```

### 2.4 文档字符串

**✅ 推荐**:
```python
def create_user(db: Session, user: UserCreate) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user: 用户创建数据
    
    Returns:
        创建的用户对象
    
    Raises:
        ValueError: 用户名已存在
    """
    # 检查用户名
    if db.query(User).filter(User.username == user.username).first():
        raise ValueError("用户名已存在")
    
    # 创建用户
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

---

## 3. 数据库设计

### 3.1 命名约定

**✅ 推荐**:
```python
# 表名：小写复数
__tablename__ = "users"
__tablename__ = "order_items"

# 字段名：小写下划线
created_at: Mapped[datetime]
user_id: Mapped[int]
is_active: Mapped[bool]

# 索引名：表名_字段名_idx
Index('users_username_idx', 'username')

# 外键名：表名_字段名_fkey
ForeignKeyConstraint(['user_id'], ['users.id'], name='orders_user_id_fkey')
```

### 3.2 审计字段

**✅ 推荐**:
```python
class AuditMixin:
    """审计字段 Mixin"""
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=func.now(),
        comment="更新时间"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        comment="创建人"
    )

class Article(Base, AuditMixin):
    __tablename__ = "articles"
    # 自动包含审计字段
```

### 3.3 软删除

**✅ 推荐**:
```python
class SoftDeleteMixin:
    """软删除 Mixin"""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        default=None,
        comment="删除时间"
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        comment="是否删除"
    )

class Article(Base, SoftDeleteMixin):
    __tablename__ = "articles"

# 查询时过滤已删除
def get_articles(db: Session):
    return db.query(Article).filter(Article.is_deleted == False).all()

# 软删除
def soft_delete_article(db: Session, article: Article):
    article.is_deleted = True
    article.deleted_at = datetime.utcnow()
    db.commit()
```

### 3.4 索引策略

**✅ 推荐**:
```python
class User(Base):
    __tablename__ = "users"
    
    # 主键自动索引
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 唯一字段自动索引
    username: Mapped[str] = mapped_column(unique=True)
    
    # 常用查询字段添加索引
    email: Mapped[str] = mapped_column(index=True)
    
    # 外键添加索引
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    
    # 组合索引
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
    )
```

---

## 4. API 设计

### 4.1 RESTful 规范

**✅ 推荐**:
```python
# 资源命名：复数名词
GET    /api/v1/articles          # 列表
POST   /api/v1/articles          # 创建
GET    /api/v1/articles/{id}     # 详情
PUT    /api/v1/articles/{id}     # 更新
DELETE /api/v1/articles/{id}     # 删除

# 关联资源
GET    /api/v1/articles/{id}/comments  # 文章的评论

# 批量操作
POST   /api/v1/articles/batch/delete   # 批量删除
```

**❌ 避免**:
```python
# 动词命名
GET  /api/v1/getArticles
POST /api/v1/createArticle
POST /api/v1/deleteArticle

# 不一致命名
GET  /api/v1/article      # 单数
GET  /api/v1/articles     # 复数（应统一）
```

### 4.2 分页参数

**✅ 推荐**:
```python
@router.get("", response_model=PaginatedResponse[ArticleResponse])
def list_articles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    total = db.query(Article).count()
    items = db.query(Article).offset(skip).limit(page_size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
```

### 4.3 搜索和过滤

**✅ 推荐**:
```python
@router.get("")
def list_articles(
    # 搜索
    search: Optional[str] = Query(None, description="搜索关键词"),
    # 过滤
    status: Optional[str] = Query(None, description="状态"),
    author_id: Optional[int] = Query(None, description="作者ID"),
    # 排序
    order_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    # 分页
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Article)
    
    # 搜索
    if search:
        query = query.filter(Article.title.contains(search))
    
    # 过滤
    if status:
        query = query.filter(Article.status == status)
    if author_id:
        query = query.filter(Article.author_id == author_id)
    
    # 排序
    if order == "asc":
        query = query.order_by(getattr(Article, order_by))
    else:
        query = query.order_by(getattr(Article, order_by).desc())
    
    # 分页
    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()
    
    return PaginatedResponse(items=items, total=total, ...)
```

### 4.4 版本化

**✅ 推荐**:
```python
# app/api/v1/articles.py
router = APIRouter(prefix="/api/v1/articles", tags=["Articles V1"])

# app/api/v2/articles.py
router = APIRouter(prefix="/api/v2/articles", tags=["Articles V2"])

# app/main.py
from app.api.v1 import articles as articles_v1
from app.api.v2 import articles as articles_v2

app.include_router(articles_v1.router)
app.include_router(articles_v2.router)
```

---

## 5. 认证和安全

### 5.1 密码安全

**✅ 推荐**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """哈希密码（bcrypt）"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

# 密码复杂度验证
def validate_password(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 8:
        raise ValueError("密码至少 8 个字符")
    if not any(c.isdigit() for c in password):
        raise ValueError("密码必须包含数字")
    if not any(c.isalpha() for c in password):
        raise ValueError("密码必须包含字母")
    return True
```

**❌ 避免**:
```python
# 明文存储
user.password = password  # 危险！

# 简单哈希
user.password = hashlib.md5(password.encode()).hexdigest()  # 不安全！
```

### 5.2 JWT 配置

**✅ 推荐**:
```python
# config.py
SECRET_KEY = "your-secret-key-min-32-characters-long"  # 至少 32 字符
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30   # 短期
REFRESH_TOKEN_EXPIRE_DAYS = 7      # 长期

# 生成强密钥
import secrets
SECRET_KEY = secrets.token_urlsafe(32)
```

**❌ 避免**:
```python
SECRET_KEY = "123456"  # 太弱！
ACCESS_TOKEN_EXPIRE_MINUTES = 999999  # 太长！
```

### 5.3 敏感信息

**✅ 推荐**:
```python
# 不返回敏感字段
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    # 不包含 password_hash

# 日志脱敏
logger.info(f"User login: {username}")  # ✅
logger.info(f"Password: {password}")    # ❌ 不记录密码

# 环境变量
DATABASE_URL = os.getenv("DATABASE_URL")  # ✅
DATABASE_URL = "postgresql://..."         # ❌ 不硬编码
```

### 5.4 CORS 配置

**✅ 推荐**:
```python
from fastapi.middleware.cors import CORSMiddleware

# 生产环境：限制来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 指定域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 开发环境：允许所有（仅开发）
if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

---

## 6. 错误处理

### 6.1 HTTP 异常

**✅ 推荐**:
```python
from fastapi import HTTPException, status

@router.get("/{id}")
def get_article(id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {id} not found"
        )
    return article

@router.post("")
def create_article(data: ArticleCreate, db: Session = Depends(get_db)):
    # 验证唯一性
    if db.query(Article).filter(Article.title == data.title).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article title already exists"
        )
    # 创建...
```

### 6.2 全局异常处理

**✅ 推荐**:
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 6.3 验证错误

**✅ 推荐**:
```python
from pydantic import BaseModel, Field, field_validator

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v.strip() == "":
            raise ValueError("Title cannot be empty")
        if "禁词" in v:
            raise ValueError("Title contains forbidden words")
        return v
```

---

## 7. 性能优化

### 7.1 数据库查询

**✅ 推荐**:
```python
# 避免 N+1 查询
from sqlalchemy.orm import joinedload

# ❌ N+1 查询
articles = db.query(Article).all()
for article in articles:
    author = article.author  # 每次都查询数据库

# ✅ 预加载
articles = db.query(Article).options(
    joinedload(Article.author)
).all()

# 只选择需要的字段
articles = db.query(
    Article.id,
    Article.title,
    Article.created_at
).all()

# 批量操作
db.bulk_insert_mappings(Article, articles_data)
db.commit()
```

### 7.2 缓存

**✅ 推荐**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_system_config(key: str, db: Session) -> Optional[str]:
    """缓存系统配置"""
    config = db.query(SystemConfig).filter(
        SystemConfig.key == key
    ).first()
    return config.value if config else None

# Redis 缓存（可选）
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

def get_article_cached(article_id: int, db: Session):
    # 尝试从缓存获取
    cached = cache.get(f"article:{article_id}")
    if cached:
        return json.loads(cached)
    
    # 从数据库查询
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        # 写入缓存（5 分钟）
        cache.setex(
            f"article:{article_id}",
            300,
            json.dumps(article, default=str)
        )
    return article
```

### 7.3 异步操作

**✅ 推荐**:
```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    """发送邮件（耗时操作）"""
    # 发送邮件逻辑...
    pass

@router.post("/users")
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 创建用户
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    
    # 后台发送欢迎邮件
    background_tasks.add_task(
        send_email,
        user.email,
        "Welcome!"
    )
    
    return db_user
```

---

## 8. 测试策略

### 8.1 单元测试

**✅ 推荐**:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    """测试登录"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_users_unauthorized():
    """测试未授权访问"""
    response = client.get("/api/users")
    assert response.status_code == 401

def test_create_article():
    """测试创建文章"""
    # 先登录
    login_response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # 创建文章
    response = client.post(
        "/api/v1/articles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Article",
            "content": "Test content",
            "author": "admin"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Article"
```

### 8.2 测试数据库

**✅ 推荐**:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# 测试数据库
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db():
    """测试数据库会话"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    """测试创建用户"""
    user = User(username="test", email="test@example.com")
    db.add(user)
    db.commit()
    
    assert user.id is not None
    assert user.username == "test"
```

---

## 9. 部署建议

### 9.1 环境分离

**✅ 推荐**:
```
.env.dev       # 开发环境
.env.test      # 测试环境
.env.prod      # 生产环境

# 加载对应环境配置
ENV = os.getenv("ENV", "dev")
load_dotenv(f".env.{ENV}")
```

### 9.2 日志配置

**✅ 推荐**:
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # 控制台输出
        logging.StreamHandler(),
        # 文件输出（轮转）
        RotatingFileHandler(
            'app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
    ]
)

logger = logging.getLogger(__name__)
```

### 9.3 健康检查

**✅ 推荐**:
```python
@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """数据库健康检查"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

---

## 📚 参考资源

- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **SQLAlchemy 文档**: https://docs.sqlalchemy.org/
- **Pydantic 文档**: https://docs.pydantic.dev/
- **Python PEP 8**: https://pep8.org/

---

**版本**: v1.0.0  
**更新**: 2026-01-01
