# 常见问题 (FAQ)

**FastAPI Scaffold 常见问题解答**

---

## 📋 目录

1. [安装和环境](#1-安装和环境)
2. [CLI 工具](#2-cli-工具)
3. [认证和权限](#3-认证和权限)
4. [数据库](#4-数据库)
5. [API 开发](#5-api-开发)
6. [部署](#6-部署)
7. [故障排查](#7-故障排查)

---

## 1. 安装和环境

### Q: 支持哪些 Python 版本？

**A**: Python 3.10 及以上版本。推荐使用 Python 3.10 或 3.11。

```bash
# 检查版本
python --version

# 如果版本过低，请升级
# Windows: 从 python.org 下载安装
# macOS: brew install python@3.10
# Linux: sudo apt install python3.10
```

### Q: 如何创建虚拟环境？

**A**: 使用 venv 或 conda：

```bash
# 方式 1: venv（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 方式 2: conda
conda create -n myproject python=3.10
conda activate myproject
```

### Q: pip install 失败怎么办？

**A**: 常见解决方案：

```bash
# 1. 升级 pip
python -m pip install --upgrade pip

# 2. 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 3. 安装特定依赖失败
pip install <package> --no-cache-dir

# 4. Windows 用户可能需要 Visual C++ Build Tools
# 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

---

## 2. CLI 工具

### Q: 如何使用 CLI 工具？

**A**: CLI 工具位于 `cli/main.py`：

```bash
# 查看帮助
python cli/main.py --help

# 创建项目
python cli/main.py init my-project

# 生成模块
python cli/main.py generate crud article --fields="title:str,content:text"

# 数据库管理
python cli/main.py db init
```

### Q: 生成代码后如何使用？

**A**: 生成后需要注册路由：

```python
# 1. 在 app/main.py 中添加
from app.api.v1 import articles

app.include_router(articles.router)

# 2. 重置数据库
python cli/main.py db reset --backup

# 3. 重启服务器
uvicorn app.main:app --reload
```

### Q: 支持哪些字段类型？

**A**: 支持 11 种字段类型：

```yaml
基础类型:
  str       # 字符串（255 字符）
  text      # 长文本
  int       # 整数
  float     # 浮点数
  bool      # 布尔值

日期时间:
  date      # 日期
  datetime  # 日期时间

特殊类型:
  json      # JSON
  email     # 邮箱（带验证）
  url       # URL（带验证）
  phone     # 电话（带验证）

可选字段: 在类型后加 ?
  title:str?  # 可选字符串
```

### Q: 如何生成带关系的模块？

**A**: 使用外键字段：

```bash
# 生成评论模块，关联到文章
python cli/main.py generate crud comment \
  --fields="content:text,article_id:int,author:str"

# 手动添加关系（编辑 Model）
# app/models/comment.py
article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
article: Mapped["Article"] = relationship(back_populates="comments")
```

---

## 3. 认证和权限

### Q: 默认用户名和密码是什么？

**A**: 

```
用户名: admin
密码: admin123
```

**生产环境务必修改！**

### Q: 如何创建新用户？

**A**: 有两种方式：

```bash
# 方式 1: 使用 API
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "email": "user@example.com",
    "role_id": 2
  }'

# 方式 2: 修改 scripts/init_db.py 添加种子数据
```

### Q: JWT Token 有效期多久？

**A**: 

```yaml
Access Token: 30 分钟
Refresh Token: 7 天

# 修改配置（.env）
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Q: 如何刷新 Token？

**A**: 

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

### Q: 如何添加新权限？

**A**: 

```python
# 1. 在 scripts/init_db.py 中添加
permissions = [
    Permission(resource="article", action="read"),
    Permission(resource="article", action="create"),
    # 添加新权限
    Permission(resource="article", action="publish"),
]

# 2. 重置数据库
python cli/main.py db reset --backup

# 3. 分配权限给角色
# 使用 API 或直接在数据库中添加
```

### Q: 如何禁用某个 API 的认证？

**A**: 

```python
# 不使用 get_current_user 依赖
@router.get("/public")
def public_endpoint():
    """公开端点（无需认证）"""
    return {"message": "This is public"}

# 使用认证的端点
@router.get("/protected")
def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    """受保护端点（需要认证）"""
    return {"message": f"Hello {current_user.username}"}
```

---

## 4. 数据库

### Q: 支持哪些数据库？

**A**: 

```yaml
开发: SQLite（默认）
生产: PostgreSQL, MySQL, MariaDB

# 修改 database.py
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# 或
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

### Q: 如何重置数据库？

**A**: 

```bash
# 使用 CLI（推荐，会备份）
python cli/main.py db reset --backup

# 手动删除（不推荐）
rm app.db
python scripts/init_db.py
```

### Q: 如何查看数据库内容？

**A**: 

```bash
# SQLite
sqlite3 app.db
.tables              # 查看所有表
SELECT * FROM users; # 查询用户表
.quit                # 退出

# PostgreSQL
psql -U user -d dbname
\dt                  # 查看所有表
SELECT * FROM users; # 查询
\q                   # 退出

# 或使用 GUI 工具
# SQLite: DB Browser for SQLite
# PostgreSQL: pgAdmin, DBeaver
```

### Q: 如何备份数据库？

**A**: 

```bash
# SQLite（简单复制）
cp app.db app.db.backup

# 使用 CLI（自动备份）
python cli/main.py db reset --backup

# PostgreSQL
pg_dump dbname > backup.sql

# MySQL
mysqldump dbname > backup.sql
```

### Q: 如何迁移数据库？

**A**: 目前使用简单的重置方式。生产环境推荐使用 Alembic：

```bash
# 安装 Alembic
pip install alembic

# 初始化
alembic init migrations

# 生成迁移
alembic revision --autogenerate -m "Add article table"

# 应用迁移
alembic upgrade head
```

---

## 5. API 开发

### Q: 如何添加自定义业务逻辑？

**A**: 

```python
# 在生成的 CRUD 文件中添加
# app/crud/article.py

class ArticleCRUD:
    # 生成的基础方法
    def get_list(self, db: Session, skip: int, limit: int):
        ...
    
    # 添加自定义方法
    def get_published_articles(self, db: Session):
        """获取已发布的文章"""
        return db.query(Article).filter(
            Article.published == True
        ).all()
    
    def get_articles_by_author(self, db: Session, author_id: int):
        """获取某作者的所有文章"""
        return db.query(Article).filter(
            Article.author_id == author_id
        ).all()

# 在 API 中使用
@router.get("/published")
def get_published_articles(db: Session = Depends(get_db)):
    return article_crud.get_published_articles(db)
```

### Q: 如何处理文件上传？

**A**: 

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # 保存文件
    contents = await file.read()
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)
    
    return {
        "filename": file.filename,
        "size": len(contents)
    }
```

### Q: 如何返回自定义错误信息？

**A**: 

```python
from fastapi import HTTPException, status

@router.post("")
def create_article(data: ArticleCreate, db: Session = Depends(get_db)):
    # 检查标题是否已存在
    if db.query(Article).filter(Article.title == data.title).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标题已存在"
        )
    
    # 创建文章
    article = Article(**data.model_dump())
    db.add(article)
    db.commit()
    return article
```

### Q: 如何实现搜索功能？

**A**: 

```python
@router.get("")
def list_articles(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Article)
    
    if search:
        # 模糊搜索标题和内容
        query = query.filter(
            (Article.title.contains(search)) |
            (Article.content.contains(search))
        )
    
    return query.all()
```

---

## 6. 部署

### Q: 如何部署到生产环境？

**A**: 推荐使用 Docker：

```bash
# 1. 创建 Dockerfile（见 TUTORIAL.md）
# 2. 构建镜像
docker build -t my-api .

# 3. 运行容器
docker run -d -p 8000:8000 my-api

# 或使用 docker-compose（推荐）
docker-compose up -d
```

### Q: 生产环境需要修改什么？

**A**: 

```bash
# 1. 修改 .env
SECRET_KEY=<生成强密钥>
DEBUG=False
DATABASE_URL=postgresql://...

# 2. 使用生产数据库（PostgreSQL）
# 3. 配置 Nginx 反向代理
# 4. 启用 HTTPS（Let's Encrypt）
# 5. 配置日志（见 BEST_PRACTICES.md）
# 6. 修改默认密码
```

### Q: 如何配置 HTTPS？

**A**: 使用 Nginx + Let's Encrypt：

```bash
# 1. 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 2. 获取证书
sudo certbot --nginx -d yourdomain.com

# 3. Nginx 配置会自动更新
# 4. 设置自动续期
sudo certbot renew --dry-run
```

### Q: 如何监控应用运行状态？

**A**: 

```python
# 1. 添加健康检查端点（已有）
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 2. 使用监控工具
# - Prometheus + Grafana
# - Sentry（错误追踪）
# - New Relic（APM）

# 3. 日志监控
# - ELK Stack (Elasticsearch + Logstash + Kibana)
# - Loki + Grafana
```

---

## 7. 故障排查

### Q: 启动时报错 "No module named 'app'"

**A**: 

```bash
# 确认当前目录
pwd  # 应该在项目根目录

# 确认虚拟环境已激活
which python  # 应该显示 venv 路径

# 重新安装依赖
pip install -r requirements.txt
```

### Q: 数据库连接失败

**A**: 

```bash
# 检查数据库文件
ls app.db

# 如果不存在，初始化
python cli/main.py db init

# 检查 DATABASE_URL
cat .env | grep DATABASE_URL

# PostgreSQL: 检查服务是否运行
sudo systemctl status postgresql
```

### Q: Token 验证失败 "Could not validate credentials"

**A**: 

```bash
# 1. 检查 SECRET_KEY
cat .env | grep SECRET_KEY

# 2. 检查 Token 是否过期
# Access Token: 30 分钟
# Refresh Token: 7 天

# 3. 重新登录获取新 Token
curl -X POST http://localhost:8000/api/auth/login \
  -d '{"username":"admin","password":"admin123"}'
```

### Q: API 返回 500 错误

**A**: 

```bash
# 1. 查看日志
# 开发模式：控制台输出
# 生产模式：查看日志文件

# 2. 开启调试模式
# .env
DEBUG=True

# 3. 检查数据库连接
python -c "from app.database import engine; print(engine)"

# 4. 检查依赖是否完整
pip list
```

### Q: CORS 错误

**A**: 

```python
# 在 app/main.py 中配置 CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q: 端口被占用

**A**: 

```bash
# 查找占用端口的进程
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或使用其他端口
uvicorn app.main:app --port 8001
```

---

## 💡 更多帮助

### 文档

- **快速开始**: `QUICK_START.md`
- **完整教程**: `TUTORIAL.md`
- **最佳实践**: `BEST_PRACTICES.md`
- **CLI 文档**: `cli/README.md`

### 社区

- **GitHub Issues**: 报告 Bug 或提问
- **GitHub Discussions**: 讨论和分享
- **Stack Overflow**: 搜索相关问题

### 联系方式

- **Email**: support@example.com
- **文档**: https://docs.example.com

---

**版本**: v1.0.0  
**更新**: 2026-01-01
