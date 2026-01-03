# FastAPI Scaffold 完整教程

**从零到一，30 分钟掌握 FastAPI Scaffold**

---

## 📖 目录

1. [环境准备](#1-环境准备)
2. [创建第一个项目](#2-创建第一个项目)
3. [理解项目结构](#3-理解项目结构)
4. [认证系统](#4-认证系统)
5. [添加业务模块](#5-添加业务模块)
6. [数据库操作](#6-数据库操作)
7. [权限控制](#7-权限控制)
8. [测试 API](#8-测试-api)
9. [部署上线](#9-部署上线)

---

## 1. 环境准备

### 1.1 安装 Python

```bash
# 检查 Python 版本（需要 3.10+）
python --version

# 如果版本过低，请安装新版本
# Windows: https://www.python.org/downloads/
# macOS: brew install python@3.10
# Linux: sudo apt install python3.10
```

### 1.2 克隆项目

```bash
# 克隆项目（假设已有代码库）
git clone <repository-url>
cd backend/fastapi-scaffold
```

### 1.3 安装 CLI 依赖

```bash
# 进入项目根目录
cd fastapi-scaffold

# 安装 CLI 依赖
pip install -r cli/requirements.txt
```

---

## 2. 创建第一个项目

### 2.1 使用 CLI 初始化

```bash
# 创建博客项目
python cli/main.py init my-blog

# 输出
Creating project...
  [1/5] Copying template files...        # 复制模板
  [2/5] Configuring database (sqlite)... # 配置数据库
  [3/5] Creating .env file...            # 创建环境变量
  [4/5] Creating README...               # 创建说明文档
  [5/5] Done!

[OK] Project created successfully!
```

### 2.2 安装项目依赖

```bash
# 进入项目目录
cd my-blog

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

### 2.3 初始化数据库

```bash
# 运行数据库初始化脚本
python ../cli/main.py db init

# 输出
Initializing database...
  Running init_db.py...
  [OK] Database initialized

Created tables:
  - users (用户表)
  - roles (角色表)
  - permissions (权限表)
  - refresh_tokens (刷新令牌表)
  - operation_logs (操作日志表)
  - dict_types (字典类型表)
  - dict_data (字典数据表)
  - system_configs (系统配置表)

Seed data:
  - Admin user: admin / admin123
  - 3 roles: admin, user, guest
  - 15+ permissions
```

### 2.4 启动服务器

```bash
# 启动开发服务器（热重载）
uvicorn app.main:app --reload

# 输出
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 2.5 访问 API 文档

打开浏览器访问:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

你会看到所有可用的 API 端点！

---

## 3. 理解项目结构

### 3.1 目录结构

```
my-blog/
├── app/                        # 应用主目录
│   ├── main.py                # 应用入口
│   ├── database.py            # 数据库连接
│   │
│   ├── core/                  # 核心模块
│   │   ├── config.py         # 配置管理
│   │   ├── security.py       # 安全（JWT/密码）
│   │   └── casbin_enforcer.py # 权限引擎
│   │
│   ├── models/               # SQLAlchemy 模型
│   │   ├── user.py          # 用户模型
│   │   ├── role.py          # 角色模型
│   │   └── ...
│   │
│   ├── schemas/              # Pydantic Schema
│   │   ├── user.py          # 用户 Schema
│   │   ├── pagination.py    # 分页 Schema
│   │   └── common.py        # 通用 Schema
│   │
│   ├── crud/                 # 数据库操作（未来）
│   │   └── ...
│   │
│   ├── api/                  # API 路由
│   │   ├── auth.py          # 认证（登录/登出）
│   │   ├── users.py         # 用户管理
│   │   ├── roles.py         # 角色管理
│   │   └── v1/              # V1 API 版本
│   │       └── ...
│   │
│   └── utils/               # 工具函数
│       ├── encryption.py    # 加密工具
│       └── ...
│
├── casbin/                   # Casbin 配置
│   ├── model.conf           # RBAC 模型
│   └── policy.csv           # 初始策略
│
├── scripts/                  # 脚本
│   └── init_db.py           # 数据库初始化
│
├── .env                      # 环境变量（不提交）
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
└── README.md                # 项目说明
```

### 3.2 核心文件说明

#### main.py - 应用入口

```python
from fastapi import FastAPI
from app.api import auth, users, roles, permissions
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 注册路由
app.include_router(auth.router, tags=["认证"])
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(roles.router, prefix=settings.API_V1_STR)
# ...
```

#### database.py - 数据库连接

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    """数据库依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### config.py - 配置管理

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Scaffold"
    API_V1_STR: str = "/api"
    
    # JWT 配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 4. 认证系统

### 4.1 登录获取 Token

```bash
# 使用 curl
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# 返回
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4.2 使用 Token 访问 API

```bash
# 设置 Token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 获取当前用户信息
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer $TOKEN"

# 获取用户列表
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN"
```

### 4.3 刷新 Token

```bash
# 使用 Refresh Token 刷新
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'

# 返回新的 Access Token
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4.4 登出

```bash
# 登出（单设备）
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# 登出（所有设备）
curl -X POST http://localhost:8000/api/auth/logout-all \
  -H "Authorization: Bearer $TOKEN"
```

---

## 5. 添加业务模块

### 5.1 使用 CLI 生成 CRUD

```bash
# 生成文章模块
python ../cli/main.py generate crud article \
  --fields="title:str,content:text,author:str,published:bool?" \
  --api

# 输出
Generating CRUD module: article
  Class name: Article
  Fields: 4

[1/3] Generating Model...
  [OK] Created app/models/article.py

[2/3] Generating Schema...
  [OK] Created app/schemas/article.py

[3/3] Generating CRUD...
  [OK] Created app/crud/article.py

Generating API routes...
  [OK] Created app/api/v1/articles.py

[OK] CRUD module generated successfully!

Next steps:
  1. Register route in app/main.py
  2. Update database: python ../cli/main.py db reset --backup
  3. Test API: curl http://localhost:8000/api/v1/articles
```

### 5.2 注册路由

编辑 `app/main.py`:

```python
# 导入新路由
from app.api.v1 import articles

# 注册路由
app.include_router(articles.router)
```

### 5.3 重置数据库

```bash
# 重置数据库（会备份旧数据）
python ../cli/main.py db reset --backup

# 输出
Backing up database...
  [OK] Backup created: app.db.backup_20260101_120000

Resetting database...
  Deleting app.db...
  Running init_db.py...
  [OK] Database reset complete
```

### 5.4 测试新 API

```bash
# 重启服务器
uvicorn app.main:app --reload

# 创建文章
curl -X POST http://localhost:8000/api/v1/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的第一篇文章",
    "content": "这是内容...",
    "author": "admin",
    "published": true
  }'

# 获取文章列表
curl http://localhost:8000/api/v1/articles \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. 数据库操作

### 6.1 查看生成的 Model

`app/models/article.py`:

```python
from sqlalchemy import String, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database import Base

class Article(Base):
    """Article 模型"""
    __tablename__ = "articles"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # 业务字段
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(255))
    published: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # 审计字段
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
```

### 6.2 查看生成的 Schema

`app/schemas/article.py`:

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ArticleBase(BaseModel):
    """Article 基础 Schema"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=255)
    published: Optional[bool] = Field(None)

class ArticleCreate(ArticleBase):
    """Article 创建 Schema"""
    pass

class ArticleUpdate(BaseModel):
    """Article 更新 Schema（所有字段可选）"""
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    published: Optional[bool] = Field(None)
    
    model_config = ConfigDict(extra='forbid')

class ArticleResponse(ArticleBase):
    """Article 响应 Schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)
```

### 6.3 添加关系字段

如果要添加作者关联（User 表）：

编辑 `app/models/article.py`:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Article(Base):
    # ... 其他字段
    
    # 外键
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # 关系
    author: Mapped["User"] = relationship(back_populates="articles")
```

编辑 `app/models/user.py`:

```python
class User(Base):
    # ... 其他字段
    
    # 关系
    articles: Mapped[List["Article"]] = relationship(back_populates="author")
```

---

## 7. 权限控制

### 7.1 理解 RBAC

**角色**:
- `admin`: 管理员（所有权限）
- `user`: 普通用户（基础权限）
- `guest`: 访客（只读权限）

**权限**:
- `user:read` - 查看用户
- `user:create` - 创建用户
- `user:update` - 更新用户
- `user:delete` - 删除用户
- `role:*` - 所有角色权限

### 7.2 Casbin 模型

`casbin/model.conf`:

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act || \
    g(r.sub, p.sub) && r.obj == p.obj && p.act == "*"
```

### 7.3 检查权限

```python
from app.core.casbin_enforcer import enforcer

# 检查权限
allowed = enforcer.enforce("admin", "user", "read")
# True

allowed = enforcer.enforce("guest", "user", "delete")
# False
```

### 7.4 API 权限装饰器

```python
from app.core.dependencies import require_permission

@router.delete("/{id}")
@require_permission("user", "delete")
def delete_user(
    id: int,
    current_user: User = Depends(get_current_user)
):
    # 只有有权限的用户能访问
    ...
```

---

## 8. 测试 API

### 8.1 使用 Swagger UI

1. 打开 http://localhost:8000/docs
2. 点击 "Authorize" 按钮
3. 输入 Token: `Bearer <your-token>`
4. 点击 "Authorize"
5. 现在可以直接测试所有 API！

### 8.2 使用 curl

```bash
# 设置变量
API="http://localhost:8000"
TOKEN="eyJhbGc..."

# 创建文章
curl -X POST $API/api/v1/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文章",
    "content": "这是测试内容",
    "author": "admin"
  }'

# 获取列表（分页）
curl "$API/api/v1/articles?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# 获取详情
curl $API/api/v1/articles/1 \
  -H "Authorization: Bearer $TOKEN"

# 更新文章
curl -X PUT $API/api/v1/articles/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "更新后的标题"}'

# 删除文章
curl -X DELETE $API/api/v1/articles/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 8.3 使用 Python requests

```python
import requests

API = "http://localhost:8000"

# 登录
response = requests.post(f"{API}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]

# 设置 headers
headers = {"Authorization": f"Bearer {token}"}

# 创建文章
response = requests.post(
    f"{API}/api/v1/articles",
    headers=headers,
    json={
        "title": "Python 测试",
        "content": "使用 requests 创建",
        "author": "admin"
    }
)
article = response.json()
print(f"创建文章 ID: {article['id']}")

# 获取列表
response = requests.get(f"{API}/api/v1/articles", headers=headers)
articles = response.json()
print(f"文章总数: {articles['total']}")
```

---

## 9. 部署上线

### 9.1 环境变量配置

创建生产环境配置 `.env.prod`:

```bash
# 应用配置
PROJECT_NAME="My Blog Production"
DEBUG=False

# 数据库（PostgreSQL）
DATABASE_URL=postgresql://user:password@localhost/mydb

# JWT 密钥（务必修改）
SECRET_KEY=<生成的强密钥>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS（根据需要配置）
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

### 9.2 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db/mydb
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

启动：

```bash
docker-compose up -d
```

### 9.3 使用 Nginx

Nginx 配置 `/etc/nginx/sites-available/myapp`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9.4 使用 Supervisor

Supervisor 配置 `/etc/supervisor/conf.d/myapp.conf`:

```ini
[program:myapp]
directory=/path/to/my-blog
command=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
autostart=true
autorestart=true
stderr_logfile=/var/log/myapp/err.log
stdout_logfile=/var/log/myapp/out.log
```

启动：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start myapp
```

---

## 🎉 完成！

恭喜！你已经完成了 FastAPI Scaffold 的完整教程。

### 你学会了:

- ✅ 创建 FastAPI 项目
- ✅ 理解项目结构
- ✅ 使用认证系统
- ✅ 生成业务模块
- ✅ 数据库操作
- ✅ 权限控制
- ✅ 测试 API
- ✅ 部署上线

### 下一步:

- **最佳实践**: 查看 `BEST_PRACTICES.md`
- **示例项目**: 查看 `examples/`
- **API 参考**: 查看自动生成的文档
- **进阶功能**: 学习 Droid 系统

---

**版本**: v1.0.0  
**更新**: 2026-01-01
