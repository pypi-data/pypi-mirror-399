# FastAPI-RBAC-Scaffold

**企业级 FastAPI 脚手架** - 开箱即用的 JWT + RBAC 权限管理系统

---

## 🎯 特性

```yaml
核心功能:
  ✅ JWT 认证（Access Token 30min + Refresh Token 7 days）
  ✅ Casbin RBAC 权限管理
  ✅ 用户/角色/权限体系
  ✅ 操作日志审计
  ✅ 字典管理
  ✅ 系统配置
  ✅ 仪表盘统计

技术特点:
  ✅ SQLAlchemy 2.0 Mapped 类型
  ✅ Pydantic 2.0 数据验证
  ✅ mypy 类型检查支持
  ✅ OpenAPI 3.0 自动文档
  ✅ CORS 跨域支持
  ✅ 分层架构清晰
```

---

## 📦 技术栈

```python
# 核心框架
FastAPI 0.104+          # Web 框架（异步）
SQLAlchemy 2.0+         # ORM（Mapped 类型）
Pydantic 2.0+           # 数据验证

# 数据库
SQLite                  # 开发数据库
PostgreSQL              # 生产数据库（可选）

# 认证授权
JWT                     # 认证（RFC 7519）
Casbin                  # 权限管理（RBAC）
bcrypt                  # 密码哈希
python-jose             # JWT 实现
cryptography            # AES-256 加密

# 工具
Uvicorn                 # ASGI 服务器
mypy                    # 类型检查
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# 修改 SECRET_KEY 和 ENCRYPTION_KEY（必须）
```

### 3. 初始化数据库

```bash
# 创建数据库表 + 初始数据
python scripts/init_db.py

# 创建管理员账号
python scripts/set_admin.py
```

### 4. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 访问文档

```
API 文档: http://localhost:8000/docs
ReDoc 文档: http://localhost:8000/redoc
健康检查: http://localhost:8000/health
```

---

## 📁 目录结构

```
.
├── app/                            # 应用核心
│   ├── api/                        # API 路由层
│   │   ├── auth.py                 # 认证 API
│   │   ├── users.py                # 用户管理
│   │   ├── roles.py                # 角色管理
│   │   ├── permissions.py          # 权限管理
│   │   ├── profile.py              # 个人信息
│   │   ├── dashboard.py            # 仪表盘
│   │   ├── dict.py                 # 字典管理
│   │   ├── enums.py                # 枚举管理
│   │   ├── examples.py             # 示例（RBAC 演示）
│   │   └── v1/                     # 业务 API（在此添加）
│   │
│   ├── models/                     # SQLAlchemy 模型
│   │   ├── user.py                 # User 模型
│   │   ├── role.py                 # Role 模型
│   │   ├── permission.py           # Permission 模型
│   │   ├── refresh_token.py        # RefreshToken 模型
│   │   ├── operation_log.py        # OperationLog 模型
│   │   ├── dict.py                 # DictType/DictData 模型
│   │   ├── system_config.py        # SystemConfig 模型
│   │   └── example.py              # Example 模型
│   │
│   ├── schemas/                    # Pydantic Schema
│   │   ├── user.py                 # User Schema
│   │   ├── role.py                 # Role Schema
│   │   ├── permission.py           # Permission Schema
│   │   ├── dict.py                 # Dict Schema
│   │   ├── system_config.py        # SystemConfig Schema
│   │   ├── dashboard.py            # Dashboard Schema
│   │   ├── example.py              # Example Schema
│   │   ├── common.py               # 通用响应类
│   │   └── pagination.py           # 分页响应
│   │
│   ├── crud/                       # CRUD 操作层
│   │   └── base.py                 # 基础 CRUD 类
│   │
│   ├── core/                       # 核心配置
│   │   ├── config.py               # 环境变量配置
│   │   ├── security.py             # JWT + 密码哈希
│   │   └── casbin_enforcer.py      # Casbin 权限引擎
│   │
│   ├── utils/                      # 工具函数
│   │   ├── encryption.py           # AES-256 加密
│   │   ├── refresh_token.py        # Token 管理
│   │   ├── operation_logger.py     # 操作日志
│   │   └── data_scope.py           # 数据权限
│   │
│   ├── database.py                 # 数据库连接
│   └── main.py                     # 应用入口
│
├── casbin/                         # Casbin 配置
│   ├── model.conf                  # RBAC 模型
│   └── policy.csv                  # 初始策略
│
├── scripts/                        # 脚本工具
│   ├── init_db.py                  # 数据库初始化
│   └── set_admin.py                # 创建管理员
│
├── requirements.txt                # Python 依赖
├── mypy.ini                        # mypy 配置
├── .env.example                    # 环境变量模板
├── .gitignore                      # Git 忽略文件
└── README.md                       # 👈 当前文件
```

---

## 🔐 认证授权

### JWT 认证流程

```
1. 登录
   POST /api/auth/login
   Body: {username, password}
   → 返回: {access_token, refresh_token, user_info}

2. 请求 API
   Header: Authorization: Bearer <access_token>
   → 验证 JWT + 权限检查

3. 刷新 Token
   POST /api/auth/refresh
   Body: {refresh_token}
   → 返回: {access_token}

4. 登出
   POST /api/auth/logout        # 登出当前设备
   POST /api/auth/logout-all    # 登出所有设备
```

### Casbin RBAC

```python
# 策略格式
p, <角色>, <资源>, <动作>
g, <用户>, <角色>

# 示例策略
p, admin, /api/users, *          # admin 可执行所有操作
p, user, /api/profile, GET       # user 可查看个人信息

g, alice, admin                  # alice 拥有 admin 角色
g, bob, user                     # bob 拥有 user 角色
```

---

## 📝 核心 API

### 认证

```
POST   /api/auth/login              # 登录
POST   /api/auth/refresh            # 刷新 Token
POST   /api/auth/logout             # 登出（当前设备）
POST   /api/auth/logout-all         # 登出（所有设备）
```

### 用户管理

```
GET    /api/users                   # 用户列表
POST   /api/users                   # 创建用户
GET    /api/users/{id}              # 用户详情
PUT    /api/users/{id}              # 更新用户
DELETE /api/users/{id}              # 删除用户
```

### 角色管理

```
GET    /api/roles                   # 角色列表
POST   /api/roles                   # 创建角色
GET    /api/roles/{id}              # 角色详情
PUT    /api/roles/{id}              # 更新角色
DELETE /api/roles/{id}              # 删除角色
POST   /api/roles/{id}/permissions  # 分配权限
```

### 权限管理

```
GET    /api/permissions             # 权限列表
POST   /api/permissions             # 创建权限
GET    /api/permissions/{id}        # 权限详情
PUT    /api/permissions/{id}        # 更新权限
DELETE /api/permissions/{id}        # 删除权限
```

### 字典管理

```
GET    /api/dict/types              # 字典类型列表
POST   /api/dict/types              # 创建字典类型
GET    /api/dict/data               # 字典数据列表
POST   /api/dict/data               # 创建字典数据
POST   /api/dict/import             # 导入字典数据
```

---

## 🛠️ 开发指南

### 添加新的业务模块

#### 1. 创建 Model

```python
# app/models/article.py
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base

class Article(Base):
    __tablename__ = "articles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

#### 2. 创建 Schema

```python
# app/schemas/article.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)

class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

#### 3. 创建 CRUD

```python
# app/crud/article.py
from app.crud.base import BaseCRUD
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate

class ArticleCRUD(BaseCRUD[Article, ArticleCreate, ArticleUpdate]):
    pass

article_crud = ArticleCRUD(Article)
```

#### 4. 创建 API

```python
# app/api/v1/articles.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.article import article_crud
from app.schemas.article import ArticleResponse, ArticleCreate
from app.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.get("", response_model=PaginatedResponse[ArticleResponse])
def list_articles(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    items, total = article_crud.get_list(db, skip=skip, limit=page_size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("", response_model=ArticleResponse)
def create_article(
    data: ArticleCreate,
    db: Session = Depends(get_db)
):
    return article_crud.create(db, obj_in=data)
```

#### 5. 注册路由

```python
# app/main.py
from app.api.v1 import articles

app.include_router(
    articles.router,
    prefix="/api/v1/articles",
    tags=["文章管理"]
)
```

---

## 🔍 类型检查

```bash
# 运行 mypy 类型检查
mypy app

# 预期结果: Success: no issues found
```

---

## 🧪 测试

```bash
# 运行测试
pytest

# 覆盖率测试
pytest --cov=app tests/
```

---

## 📚 最佳实践

### Schema 设计

```python
# 遵循四层结构
# Base → Create → Update → Response

class UserBase(BaseModel):
    """共享字段"""
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    """创建时字段"""
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    """更新时字段（所有可选）"""
    username: str | None = Field(None, min_length=3)

class UserResponse(UserBase):
    """响应字段"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

### API 设计

```python
# RESTful 规范
GET    /api/v1/resource          # 列表（分页）
POST   /api/v1/resource          # 创建
GET    /api/v1/resource/{id}     # 详情
PUT    /api/v1/resource/{id}     # 更新
DELETE /api/v1/resource/{id}     # 删除
```

### 权限控制

```python
from app.core.security import get_current_user
from app.core.casbin_enforcer import enforcer

@router.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限
    if not enforcer.enforce(current_user.username, "/api/protected", "GET"):
        raise HTTPException(403, "无权限")
    
    return {"message": "受保护的资源"}
```

---

## 🐛 常见问题

### 1. 数据库表未创建

```bash
# 删除数据库文件重新初始化
rm app.db
python scripts/init_db.py
```

### 2. JWT Token 过期

```bash
# 使用 refresh_token 刷新
POST /api/auth/refresh
Body: {"refresh_token": "<your_refresh_token>"}
```

### 3. 权限检查失败

```bash
# 检查 Casbin 策略
cat casbin/policy.csv

# 同步策略到数据库
python scripts/sync_casbin_policies.py
```

---

## 📖 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://www.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Casbin 文档](https://casbin.org/)

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎贡献代码、报告 Bug 或提出新功能建议！

---

**维护者**: 项目团队  
**版本**: v1.0.0  
**创建日期**: 2026-01-01

---

*"开箱即用的企业级 FastAPI 脚手架，专注于业务开发"*
