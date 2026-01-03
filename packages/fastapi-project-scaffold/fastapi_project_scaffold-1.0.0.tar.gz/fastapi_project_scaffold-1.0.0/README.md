# FastAPI Scaffold

**企业级 FastAPI 项目脚手架 - 5 分钟创建生产就绪的 API**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🚀 特性

- ⚡ **极速开发**: 5 分钟创建项目，30 秒生成模块
- 🤖 **AI 驱动**: 自然语言描述需求，自动生成代码
- 🔒 **生产就绪**: JWT + RBAC 认证授权，开箱即用
- 📝 **类型安全**: SQLAlchemy 2.0 + Pydantic 2.0，100% 类型提示
- 🎯 **智能推断**: 11 种字段类型，自动推断关系和约束
- ✅ **质量保证**: 44 项 CheckList 验证，迭代修复
- 📚 **完整文档**: 从入门到精通，示例项目齐全

---

## 📦 安装

```bash
pip install fastapi-project-scaffold
```

---

## 🎯 快速开始

### 方式一: CLI 工具（5 分钟）

```bash
# 创建项目
fastapi-scaffold init my-blog

# 进入项目
cd my-blog

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
fastapi-scaffold db init

# 启动服务
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档！

### 方式二: Droid 智能生成（1 分钟）

使用自然语言描述需求，Droid 自动生成完整项目：

```
创建一个博客系统，包含文章、评论和标签。
文章有标题、内容、作者、发布状态。
评论关联到文章，包含内容和作者。
标签可以关联多篇文章。
```

**结果**: 完整项目，2 个实体，10 个 API 端点，1 分钟生成！

---

## 💡 核心功能

### 1. 项目初始化

```bash
# 基础项目
fastapi-scaffold init my-project

# 使用 PostgreSQL
fastapi-scaffold init my-project --db=postgres

# 不包含示例代码
fastapi-scaffold init my-project --no-examples
```

**生成内容**:
- ✅ 完整项目结构
- ✅ JWT 认证系统
- ✅ RBAC 权限管理
- ✅ 用户角色权限
- ✅ 操作日志
- ✅ 数据库初始化
- ✅ API 文档

### 2. CRUD 生成

```bash
# 生成 CRUD 模块
fastapi-scaffold generate crud article \
  --fields="title:str,content:text,author:str,published:bool"

# 同时生成 API
fastapi-scaffold generate crud product \
  --fields="name:str,price:float,stock:int" \
  --api
```

**生成文件**:
- ✅ `app/models/article.py` - SQLAlchemy Model
- ✅ `app/schemas/article.py` - Pydantic Schema (4 层)
- ✅ `app/crud/article.py` - CRUD 操作
- ✅ `app/api/v1/articles.py` - API 路由 (5 端点)

### 3. 支持的字段类型

```yaml
基础类型:
  str, text, int, float, bool, date, datetime

特殊类型:
  json, email, url, phone

可选字段:
  title:str?  # Optional 类型
```

### 4. 智能 Droid 系统

**scaffold-generator**: 生成完整项目
- 自然语言需求解析
- 多实体并行生成
- 关系自动识别
- 完整项目集成

**module-generator**: 生成单个模块
- 智能字段推断（85-95% 准确度）
- 关系型字段处理（ForeignKey）
- 约束条件推断（unique, pattern, range）
- 自动集成到现有项目

---

## 📚 文档

- **快速开始**: [QUICK_START.md](QUICK_START.md) - 5 分钟上手
- **完整教程**: [TUTORIAL.md](TUTORIAL.md) - 30 分钟掌握
- **最佳实践**: [BEST_PRACTICES.md](BEST_PRACTICES.md) - 专业开发
- **常见问题**: [FAQ.md](FAQ.md) - 33 个问答
- **示例项目**:
  - [Blog 系统](examples/blog/) - 文章、评论、标签
  - [Todo 应用](examples/todo/) - 任务管理

---

## 🎨 示例

### 生成博客系统

```bash
fastapi-scaffold init blog-system
cd blog-system

# 生成文章模块
fastapi-scaffold generate crud article \
  --fields="title:str,content:text,published:bool?" \
  --api

# 生成评论模块
fastapi-scaffold generate crud comment \
  --fields="content:text,article_id:int,author_id:int" \
  --api

# 启动
fastapi-scaffold db init
uvicorn app.main:app --reload
```

### API 端点

```
POST   /api/auth/login          # 登录
GET    /api/profile             # 当前用户
GET    /api/users               # 用户列表
GET    /api/v1/articles         # 文章列表
POST   /api/v1/articles         # 创建文章
GET    /api/v1/articles/{id}    # 文章详情
PUT    /api/v1/articles/{id}    # 更新文章
DELETE /api/v1/articles/{id}    # 删除文章
```

### 使用示例

```python
import requests

# 登录
response = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]

# 创建文章
response = requests.post(
    "http://localhost:8000/api/v1/articles",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "title": "我的第一篇文章",
        "content": "这是内容...",
        "published": True
    }
)
article = response.json()
print(f"创建文章: {article['id']}")
```

---

## 🛠️ 技术栈

### 后端
- **FastAPI** 0.104+ - 现代高性能 Web 框架
- **SQLAlchemy** 2.0+ - ORM（Mapped 类型）
- **Pydantic** 2.0+ - 数据验证
- **JWT** - 认证（Access + Refresh Token）
- **Casbin** - RBAC 权限管理
- **bcrypt** - 密码哈希

### 开发工具
- **Click** 8.1+ - CLI 框架
- **Jinja2** 3.1+ - 模板引擎
- **mypy** - 类型检查
- **pytest** - 单元测试

---

## 📊 数据统计

```yaml
项目规模:
  文件数: 99 个
  代码行数: ~10,680 行
  文档行数: ~12,500 行
  总计: ~23,180 行

功能统计:
  CLI 命令: 5 个
  Jinja2 模板: 4 个
  智能 Droid: 2 个
  示例项目: 2 个
  文档: 9 个

开发效率:
  传统方式: ~110 分钟 / CRUD 模块
  使用 CLI: ~5 分钟 / CRUD 模块
  使用 Droid: ~1 分钟 / 完整项目
  效率提升: 22-110 倍
```

---

## 🎯 核心优势

### 1. 极致效率

```
创建项目: 30 秒
生成模块: 30 秒
完整系统: 2 分钟
```

### 2. 生产就绪

```yaml
认证授权: JWT + RBAC
类型安全: 100% mypy
代码质量: CheckList 验证
安全性: bcrypt + 敏感信息保护
```

### 3. 智能化

```yaml
自然语言: 描述需求即可
智能推断: 字段类型、关系、约束
自动验证: 44 项 CheckList
迭代修复: 最多 3 次自动修复
```

### 4. 完整文档

```yaml
入门: 5 分钟快速开始
进阶: 30 分钟完整教程
精通: 最佳实践指南
参考: 33 个常见问题
```

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包
- [Pydantic](https://docs.pydantic.dev/) - 数据验证库
- [Casbin](https://casbin.org/) - 权限管理框架
- [Click](https://click.palletsprojects.com/) - CLI 框架

---

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/btrobot/fastapi-scaffold/issues)
- **Discussions**: [GitHub Discussions](https://github.com/btrobot/fastapi-scaffold/discussions)
- **Email**: support@example.com

---

## ⭐ Star History

如果这个项目对你有帮助，请给一个 ⭐ Star！

---

**Made with ❤️ by Project Team**
