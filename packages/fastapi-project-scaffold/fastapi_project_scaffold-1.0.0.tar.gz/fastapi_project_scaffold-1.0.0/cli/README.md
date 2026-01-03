# FastAPI Scaffold CLI

企业级 FastAPI 脚手架命令行工具

---

## 🚀 快速开始

### 安装

```bash
# 方式 1: 直接运行（无需安装）
cd fastapi-scaffold
python cli/main.py --help

# 方式 2: 安装为命令（开发中）
# pip install -e .
# scaffold --help
```

---

## 📝 命令列表

### 1. init - 初始化项目

```bash
# 基础用法
python cli/main.py init my-project

# 使用 PostgreSQL
python cli/main.py init my-blog --db=postgres

# 不包含示例代码
python cli/main.py init ecommerce --no-examples

# 强制覆盖
python cli/main.py init test-app --force
```

**选项**:
- `--db [sqlite|postgres]` - 数据库类型（默认：sqlite）
- `--no-examples` - 排除示例代码
- `--force` - 覆盖已存在的目录

**输出**:
- 完整的项目结构
- 配置好的 .env 文件
- README 使用说明

---

### 2. check - 代码质量检查

```bash
# 运行所有检查
python cli/main.py check

# 只检查 Schema
python cli/main.py check --schemas

# 只运行 mypy
python cli/main.py check --mypy

# 检查代码格式
python cli/main.py check --format
```

**检查项**:
- ✅ Schema 规范（Base/Create/Update/Response）
- ✅ mypy 类型检查
- ✅ 代码格式（空行、导入等）

---

### 3. generate - 代码生成

```bash
# 生成 CRUD 模块（Model + Schema + CRUD）
python cli/main.py generate crud article --fields="title:str,content:text,author:str"

# 同时生成 API
python cli/main.py generate crud product --fields="name:str,price:float,stock:int" --api

# 可选字段（在类型后加 ?）
python cli/main.py generate crud post --fields="title:str,body:text,published:bool?"

# 只生成 API（需要先有 CRUD）
python cli/main.py generate api article --auth

# 不需要认证的 API
python cli/main.py generate api public_data --no-auth
```

**子命令**:

#### 3.1 generate crud

```bash
python cli/main.py generate crud <module> --fields="name:type,..." [options]
```

**选项**:
- `--fields` - 字段定义（必需）
- `--api` - 同时生成 API
- `--overwrite` - 覆盖已存在文件

**字段类型**:
- `str` - 字符串（String(255)）
- `text` - 长文本（Text）
- `int` - 整数（Integer）
- `float` - 浮点数（Float）
- `bool` - 布尔值（Boolean）
- `date` - 日期（Date）
- `datetime` - 日期时间（DateTime）
- `json` - JSON（JSON）
- `email` - 邮箱（String(100)）
- `url` - URL（String(500)）
- `phone` - 电话（String(20)）

**可选字段**: 在类型后添加 `?`，如 `description:text?`

**生成文件**:
- `app/models/<module>.py` - Model 类
- `app/schemas/<module>.py` - Schema 类（Base/Create/Update/Response）
- `app/crud/<module>.py` - CRUD 操作类

#### 3.2 generate api

```bash
python cli/main.py generate api <module> [options]
```

**选项**:
- `--auth/--no-auth` - 是否添加认证（默认：是）
- `--prefix` - API 路径前缀（默认：/api/v1/<module>s）
- `--tags` - OpenAPI 标签
- `--overwrite` - 覆盖已存在文件

**生成文件**:
- `app/api/v1/<module>s.py` - API 路由文件

**生成端点**:
- `GET /<module>s` - 列表（分页）
- `POST /<module>s` - 创建
- `GET /<module>s/{id}` - 详情
- `PUT /<module>s/{id}` - 更新
- `DELETE /<module>s/{id}` - 删除

---

### 4. db - 数据库管理

```bash
# 初始化数据库
python cli/main.py db init

# 重置数据库（危险）
python cli/main.py db reset

# 重置前备份
python cli/main.py db reset --backup

# 迁移（占位）
python cli/main.py db migrate
python cli/main.py db upgrade
```

**子命令**:
- `init` - 初始化数据库（创建表+种子数据）
- `reset` - 重置数据库（删除所有数据）
- `migrate` - 生成迁移文件（待实现）
- `upgrade` - 应用迁移（待实现）

---

## 🎯 使用场景

### 场景 1: 创建新项目

```bash
# 1. 初始化项目
python cli/main.py init my-blog

# 2. 进入项目
cd my-blog

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 初始化数据库
python ../cli/main.py db init

# 6. 启动服务
uvicorn app.main:app --reload
```

### 场景 2: 代码质量检查

```bash
# 进入项目目录
cd my-project

# 运行检查
python ../cli/main.py check --all

# 修复问题后重新检查
python ../cli/main.py check
```

### 场景 3: 数据库管理

```bash
# 初始化数据库
python ../cli/main.py db init

# 重置数据库（开发环境）
python ../cli/main.py db reset --backup

# 验证数据库
python -c "import sqlite3; conn = sqlite3.connect('app.db'); print('Tables:', conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"
```

---

## 📚 命令参考

### 通用选项

```bash
--help       # 显示帮助信息
--version    # 显示版本号
```

### 环境变量

```bash
# 设置项目模板路径（可选）
export SCAFFOLD_TEMPLATE_DIR=/path/to/custom/template

# 设置配置文件路径（可选）
export SCAFFOLD_CONFIG=~/.scaffold.yaml
```

---

## 🔧 高级用法

### 自定义模板

```bash
# 使用自定义模板（待实现）
python cli/main.py init my-project --template=/path/to/template
```

### 配置文件

```yaml
# scaffold.yaml（待实现）
project:
  name: my-project
  version: 1.0.0

database:
  type: sqlite

generation:
  model:
    add_created_at: true
    add_updated_at: true
```

---

## 📖 开发指南

### 添加新命令

1. 创建命令文件 `cli/commands/my_command.py`
2. 实现命令函数
3. 在 `cli/main.py` 中注册命令

```python
# cli/commands/my_command.py
import click

@click.command()
def my_command():
    """My command description"""
    click.echo("Hello!")

# cli/main.py
from cli.commands.my_command import my_command
cli.add_command(my_command)
```

### 运行测试

```bash
# 测试 init 命令
python cli/main.py init test-project --force
cd test-project
python -c "from app.main import app; print('OK')"

# 测试 check 命令
cd test-project
python ../cli/main.py check --all

# 清理测试项目
cd ..
rm -rf test-project
```

---

## 🐛 故障排查

### 问题 1: 命令not found

**症状**: `scaffold: command not found`

**解决**:
```bash
# 使用完整路径
python /path/to/fastapi-scaffold/cli/main.py init my-project

# 或创建别名
alias scaffold='python /path/to/fastapi-scaffold/cli/main.py'
```

### 问题 2: 模板not found

**症状**: `Error: Template directory not found`

**解决**:
```bash
# 确认目录结构
ls fastapi-scaffold/
# 应该看到: cli/ template/ README.md

# 从正确的位置运行
cd fastapi-scaffold
python cli/main.py init my-project
```

### 问题 3: 编码错误（Windows）

**症状**: `UnicodeEncodeError: 'gbk' codec can't encode...`

**解决**: 已修复，使用 ASCII 字符替代特殊符号

---

## 📦 版本历史

### v1.0.0 (2026-01-01)

**实现功能**:
- ✅ `init` 命令 - 项目初始化
- ✅ `check` 命令 - 代码质量检查
- ✅ `db init` 命令 - 数据库初始化
- ✅ `db reset` 命令 - 数据库重置
- ✅ `generate crud` 命令 - 生成 CRUD 模块（Model + Schema + CRUD）
- ✅ `generate api` 命令 - 生成 API 路由

**计划功能**:
- ⏳ `db migrate` - 数据库迁移
- ⏳ 交互式向导
- ⏳ 配置文件支持
- ⏳ 自定义模板支持

---

## 🤝 贡献

欢迎贡献！请提交 Issue 或 Pull Request。

---

**维护者**: 项目团队  
**版本**: v1.0.0  
**文档更新**: 2026-01-01
