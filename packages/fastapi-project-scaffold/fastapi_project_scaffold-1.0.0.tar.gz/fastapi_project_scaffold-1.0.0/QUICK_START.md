# 快速开始

**5 分钟上手 FastAPI Scaffold**

---

## 📦 环境要求

```yaml
Python: 3.10+
系统: Windows / Linux / macOS
```

---

## 🚀 方式一: CLI 工具（推荐）

### 1. 创建新项目

```bash
# 进入脚手架目录
cd fastapi-scaffold

# 初始化项目（使用 SQLite）
python cli/main.py init my-blog

# 初始化项目（使用 PostgreSQL）
python cli/main.py init my-shop --db=postgres

# 不包含示例代码
python cli/main.py init my-api --no-examples
```

**输出**:
```
Creating project...
  [1/5] Copying template files...
  [2/5] Configuring database (sqlite)...
  [3/5] Creating .env file...
  [4/5] Creating README...
  [5/5] Done!

[OK] Project created successfully!

Next steps:
  cd my-blog
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  python ../cli/main.py db init
  uvicorn app.main:app --reload
```

### 2. 安装依赖

```bash
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

### 3. 初始化数据库

```bash
# 初始化数据库（创建表 + 种子数据）
python ../cli/main.py db init
```

**输出**:
```
Initializing database...
  Running init_db.py...
  [OK] Database initialized

Created tables:
  - users
  - roles
  - permissions
  - refresh_tokens
  - operation_logs
  - dict_types
  - dict_data
  - system_configs

Seed data:
  - Admin user: admin / admin123
  - 3 roles (admin, user, guest)
  - 15+ permissions

Database: app.db
```

### 4. 启动服务器

```bash
uvicorn app.main:app --reload
```

**输出**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 5. 访问文档

打开浏览器访问:
- **API 文档**: http://localhost:8000/docs
- **备用文档**: http://localhost:8000/redoc

### 6. 测试 API

```bash
# 登录获取 Token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 返回
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}

# 使用 Token 访问受保护的 API
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## 🎨 方式二: 使用 Droid（智能生成）

### 1. 使用 scaffold-generator Droid

**在 Factory 界面中调用**:

```
请使用 scaffold-generator Droid 创建一个博客系统：

需求描述：
创建一个博客系统，包含文章和评论。
文章有标题、内容、作者、发布状态。
评论关联到文章，包含内容和作者。

项目名称：my-blog
数据库：sqlite
认证：是
```

**Droid 自动完成**:
1. ✅ 解析需求（2 个实体）
2. ✅ 推断字段（智能类型推断）
3. ✅ 生成项目
4. ✅ 生成代码（9 个文件）
5. ✅ 注册路由
6. ✅ 初始化数据库
7. ✅ 验证通过（23 项）

**结果**:
```
✅ 博客系统创建成功！

📁 项目结构:
my-blog/
├── app/
│   ├── models/         # Article, Comment
│   ├── schemas/        # Article, Comment
│   ├── crud/          # Article, Comment
│   ├── api/v1/        # articles, comments
│   └── main.py        # 已注册路由
├── .env               # 环境配置
├── app.db             # 数据库（已初始化）
└── README.md

📊 生成统计:
- 实体数: 2
- API 端点: 10
- 数据表: 2
- 代码文件: 9

🚀 快速开始:
cd my-blog
uvicorn app.main:app --reload
```

**时间**: ~1 分钟

### 2. 使用 module-generator Droid

**在已有项目中添加新模块**:

```
请使用 module-generator Droid 在当前项目中添加产品模块：

需求描述：
产品模块，包含名称、价格、库存、描述。
名称必需，最多100字符。
价格必需，大于0的浮点数。
库存必需，整数，大于等于0。
描述可选，长文本。

模块名称：product
生成 API：是
自动集成：是
```

**Droid 自动完成**:
1. ✅ 检查环境
2. ✅ 推断字段（4 个字段）
3. ✅ 生成代码（4 个文件）
4. ✅ 自动集成（3 个文件更新）
5. ✅ 验证通过（21 项）

**结果**:
```
✅ 产品模块创建成功！

📦 模块名称: product
📝 类名: Product

📁 生成文件:
- app/models/product.py
- app/schemas/product.py
- app/crud/product.py
- app/api/v1/products.py

📊 字段统计:
- 总字段数: 4
- 必需字段: 3
- 可选字段: 1

🔗 API 端点:
- GET    /api/v1/products
- POST   /api/v1/products
- GET    /api/v1/products/{id}
- PUT    /api/v1/products/{id}
- DELETE /api/v1/products/{id}

🔄 集成状态:
- ✅ models/__init__.py 已更新
- ✅ main.py 路由已注册
- ✅ README.md 已更新
```

**时间**: ~30 秒

---

## 📝 生成新模块

### 使用 CLI

```bash
# 进入项目目录
cd my-blog

# 生成 CRUD 模块
python ../cli/main.py generate crud article \
  --fields="title:str,content:text,author:str,published:bool"

# 同时生成 API
python ../cli/main.py generate crud product \
  --fields="name:str,price:float,stock:int" \
  --api

# 只生成 API（需要先有 CRUD）
python ../cli/main.py generate api article
```

### 字段类型

```yaml
基础类型:
  str        # 字符串（String(255)）
  text       # 长文本（Text）
  int        # 整数（Integer）
  float      # 浮点数（Float）
  bool       # 布尔值（Boolean）

日期时间:
  date       # 日期（Date）
  datetime   # 日期时间（DateTime）

特殊类型:
  json       # JSON（JSON）
  email      # 邮箱（String(100) + 验证）
  url        # URL（String(500) + 验证）
  phone      # 电话（String(20) + 验证）
```

### 可选字段

```bash
# 在类型后加 ? 表示可选
--fields="title:str,content:text,summary:text?"

# 生成结果
summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
summary: Optional[str] = Field(None, min_length=1)
```

---

## 🔧 常用命令

### 项目管理

```bash
# 创建项目
python cli/main.py init <project-name> [--db=sqlite|postgres] [--no-examples]

# 代码质量检查
python cli/main.py check [--schemas] [--mypy] [--format] [--all]

# 数据库管理
python cli/main.py db init                  # 初始化
python cli/main.py db reset [--backup]      # 重置
```

### 代码生成

```bash
# 生成 CRUD
python cli/main.py generate crud <module> --fields="..."

# 生成 API
python cli/main.py generate api <module> [--auth] [--no-auth]

# 完整示例
python cli/main.py generate crud article \
  --fields="title:str,content:text,author_id:int,published:bool?" \
  --api
```

### 服务器管理

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 指定配置文件
uvicorn app.main:app --env-file .env.prod
```

---

## 📚 下一步

### 学习更多

- **完整教程**: 查看 `TUTORIAL.md`
- **CLI 文档**: 查看 `cli/README.md`
- **Droid 指南**: 查看 `.factory/droids/`
- **最佳实践**: 查看 `BEST_PRACTICES.md`

### 示例项目

- **博客系统**: `examples/blog/`
- **Todo 应用**: `examples/todo/`
- **电商后台**: `examples/ecommerce/`

### 视频教程

- **快速开始** (5 分钟): [链接]
- **CLI 工具** (15 分钟): [链接]
- **Droid 系统** (20 分钟): [链接]

---

## 🆘 故障排查

### 问题 1: 无法导入模块

**症状**:
```
ModuleNotFoundError: No module named 'app'
```

**解决**:
```bash
# 确认在项目根目录
pwd  # 应该显示 /path/to/my-project

# 确认虚拟环境已激活
which python  # 应该显示 venv 路径

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 2: 数据库连接失败

**症状**:
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**解决**:
```bash
# 检查数据库文件
ls app.db

# 如果不存在，初始化数据库
python ../cli/main.py db init

# 检查 .env 文件
cat .env | grep DATABASE_URL
```

### 问题 3: JWT Token 无效

**症状**:
```
401 Unauthorized: Could not validate credentials
```

**解决**:
```bash
# 检查 .env 中的密钥
cat .env | grep SECRET_KEY

# 如果为空，生成新密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 更新 .env
echo "SECRET_KEY=<生成的密钥>" >> .env

# 重启服务器
```

### 问题 4: 端口被占用

**症状**:
```
ERROR: [Errno 48] Address already in use
```

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# 杀死进程
kill <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# 或使用其他端口
uvicorn app.main:app --port 8001
```

---

## 💡 提示

### 开发技巧

1. **使用热重载**: `--reload` 自动重启服务器
2. **查看日志**: `--log-level debug` 查看详细日志
3. **使用 API 文档**: `/docs` 直接测试 API
4. **备份数据库**: 重置前使用 `--backup`

### 最佳实践

1. **使用虚拟环境**: 避免依赖冲突
2. **版本控制**: 提交前检查 `.gitignore`
3. **环境变量**: 不要提交 `.env` 文件
4. **定期检查**: 使用 `check` 命令验证代码

---

## 🎉 成功！

现在你已经成功创建了一个 FastAPI 项目！

**可用功能**:
- ✅ JWT 认证
- ✅ RBAC 权限
- ✅ 用户管理
- ✅ 角色权限
- ✅ 操作日志
- ✅ 字典管理
- ✅ 系统配置

**下一步**:
1. 添加你的业务模块
2. 自定义 API 逻辑
3. 部署到生产环境

**需要帮助**？查看完整文档！

---

**版本**: v1.0.0  
**更新**: 2026-01-01
