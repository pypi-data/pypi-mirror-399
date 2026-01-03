# FastAPI-Scaffold CLI 工具设计

**版本**: v1.0.0  
**文档风格**: KAS v1.0.0  
**创建日期**: 2026-01-01

---

## 🎯 设计目标

```yaml
核心目标:
  - 快速初始化项目
  - 自动生成代码
  - 减少重复劳动
  - 保证代码质量

设计原则:
  - 简单易用
  - 约定优于配置
  - 可扩展
  - 向导式交互
```

---

## 🏗️ CLI 架构

```
scaffold (主命令)
├── init <project-name>           # 初始化项目
├── generate (gen/g)              # 代码生成
│   ├── crud <module>             # 生成 CRUD
│   ├── api <module>              # 生成 API
│   ├── model <module>            # 生成 Model
│   └── schema <module>           # 生成 Schema
├── db                            # 数据库管理
│   ├── init                      # 初始化数据库
│   ├── migrate                   # 生成迁移
│   ├── upgrade                   # 执行迁移
│   └── reset                     # 重置数据库
├── check                         # 代码检查
│   ├── --schemas                 # 检查 Schema
│   ├── --mypy                    # 运行 mypy
│   └── --all                     # 全部检查
├── add <feature>                 # 添加功能
│   ├── websocket                 # WebSocket 支持
│   ├── celery                    # Celery 任务队列
│   └── redis                     # Redis 缓存
└── admin                         # 管理员操作
    ├── create                    # 创建管理员
    └── reset-password            # 重置密码
```

---

## 📝 命令详细设计

### 1. init 命令

```bash
scaffold init <project-name> [options]

Options:
  --db=sqlite|postgres           # 数据库类型 (默认: sqlite)
  --auth=jwt|oauth2              # 认证方式 (默认: jwt)
  --rbac=casbin|simple           # 权限模型 (默认: casbin)
  --no-examples                  # 不包含示例代码
  --template=<path>              # 使用自定义模板

流程:
1. 检查项目名称是否合法
2. 检查目录是否已存在
3. 复制模板文件
4. 替换变量（项目名、数据库配置等）
5. 安装依赖（可选）
6. 初始化 Git（可选）
7. 打印下一步指引

示例:
  scaffold init my-blog
  scaffold init ecommerce --db=postgres --no-examples
```

**实现要点**:
```python
def init_project(name, db, auth, rbac, no_examples, template):
    # 1. 验证项目名
    if not is_valid_name(name):
        raise ValueError("Invalid project name")
    
    # 2. 检查目录
    if Path(name).exists():
        confirm = click.confirm(f"Directory {name} exists. Continue?")
        if not confirm:
            return
    
    # 3. 复制模板
    template_dir = Path(template) if template else get_default_template()
    copy_template(template_dir, name)
    
    # 4. 替换变量
    replace_variables(name, {
        'PROJECT_NAME': name,
        'DB_TYPE': db,
        'AUTH_TYPE': auth,
        'RBAC_TYPE': rbac
    })
    
    # 5. 删除示例（如果需要）
    if no_examples:
        remove_examples(name)
    
    # 6. 打印指引
    print_next_steps(name)
```

---

### 2. generate crud 命令

```bash
scaffold generate crud <module> [options]

Options:
  --fields="name:str,age:int,email:str"  # 字段定义（必需）
  --api                                   # 同时生成 API
  --test                                  # 同时生成测试
  --overwrite                             # 覆盖已存在文件

流程:
1. 解析字段定义
2. 生成 Model (app/models/<module>.py)
3. 生成 Schema (app/schemas/<module>.py)
4. 生成 CRUD (app/crud/<module>.py)
5. 更新 __init__.py
6. 如果 --api，生成 API 路由
7. 如果 --test，生成测试文件
8. 打印集成指引

示例:
  scaffold generate crud article --fields="title:str,content:text,author_id:int"
  scaffold g crud product --fields="name:str,price:float,stock:int" --api --test
```

**字段类型映射**:
```python
FIELD_TYPE_MAPPING = {
    # Python 类型 → SQLAlchemy 类型
    'str': 'String(255)',
    'text': 'Text',
    'int': 'Integer',
    'float': 'Float',
    'bool': 'Boolean',
    'date': 'Date',
    'datetime': 'DateTime',
    'json': 'JSON',
    
    # 特殊类型
    'email': 'String(100)',
    'url': 'String(500)',
    'phone': 'String(20)',
}

# Pydantic 验证器
FIELD_VALIDATORS = {
    'email': 'EmailStr',
    'url': 'HttpUrl',
    'phone': 'constr(pattern=r"^1[3-9]\\d{9}$")',
}
```

**代码模板**:
```python
# model.py.j2
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class {{ module_name|title }}(Base):
    __tablename__ = "{{ table_name }}"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    {% for field in fields %}
    {{ field.name }}: Mapped[{{ field.python_type }}] = mapped_column({{ field.sa_type }})
    {% endfor %}
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
```

---

### 3. generate api 命令

```bash
scaffold generate api <module> [options]

Options:
  --crud=<name>                   # 关联 CRUD 类（默认：同名）
  --auth                          # 添加认证装饰器
  --permission=<permission>       # 添加权限检查
  --prefix=/api/v1                # API 路径前缀（默认: /api/v1）
  --tags=<tags>                   # OpenAPI 标签

流程:
1. 检查 CRUD 类是否存在
2. 生成 API 路由文件 (app/api/v1/<module>s.py)
3. 生成标准 CRUD 端点（GET/POST/PUT/DELETE）
4. 添加认证和权限（如果指定）
5. 打印路由注册指引

示例:
  scaffold generate api article --auth --permission="article:*"
  scaffold g api user --crud=user_crud --prefix=/api/v2
```

**生成端点**:
```python
# 标准 CRUD 端点
GET    /<module>s              # 列表（分页）
POST   /<module>s              # 创建
GET    /<module>s/{id}         # 详情
PUT    /<module>s/{id}         # 更新
DELETE /<module>s/{id}         # 删除

# 可选端点
POST   /<module>s/batch/delete # 批量删除
GET    /<module>s/export       # 导出
POST   /<module>s/import       # 导入
```

---

### 4. check 命令

```bash
scaffold check [options]

Options:
  --schemas                       # 检查 Schema 规范
  --mypy                          # 运行 mypy 类型检查
  --format                        # 检查代码格式
  --all                           # 全部检查（默认）
  --fix                           # 自动修复（如果可能）

流程:
1. 根据选项执行不同检查
2. 汇总检查结果
3. 输出错误和警告
4. 返回退出码（0=成功，1=失败）

示例:
  scaffold check                   # 全部检查
  scaffold check --schemas         # 只检查 Schema
  scaffold check --mypy --fix      # 运行 mypy 并尝试修复
```

**检查项**:
```python
CHECKS = {
    'schemas': {
        'runner': run_schema_check,
        'description': 'Check Pydantic Schema conventions',
        'fixable': True
    },
    'mypy': {
        'runner': run_mypy,
        'description': 'Run mypy type checking',
        'fixable': False
    },
    'format': {
        'runner': run_format_check,
        'description': 'Check code formatting',
        'fixable': True
    },
    'imports': {
        'runner': check_imports,
        'description': 'Check import organization',
        'fixable': True
    }
}
```

---

### 5. db 命令

```bash
scaffold db <subcommand> [options]

Subcommands:
  init                            # 初始化数据库
  migrate [message]               # 生成迁移文件
  upgrade                         # 执行迁移
  downgrade                       # 回滚迁移
  reset                           # 重置数据库（危险）
  seed                            # 填充测试数据

Options:
  --yes                           # 跳过确认
  --backup                        # 先备份数据库

示例:
  scaffold db init                # 初始化数据库
  scaffold db migrate "add user table"
  scaffold db upgrade
  scaffold db reset --backup
```

**实现要点**:
```python
def db_init():
    """初始化数据库"""
    # 1. 检查数据库是否已存在
    if db_exists():
        confirm = click.confirm("Database exists. Recreate?")
        if not confirm:
            return
    
    # 2. 运行初始化脚本
    run_script("scripts/init_db.py")
    
    # 3. 验证数据
    verify_db()

def db_migrate(message):
    """生成迁移文件"""
    # 1. 检查是否有未提交的迁移
    check_pending_migrations()
    
    # 2. 生成迁移文件
    generate_migration(message)
    
    # 3. 打印文件路径
    print_migration_info()

def db_reset(backup):
    """重置数据库"""
    # 1. 确认（危险操作）
    confirm = click.confirm(
        "This will delete all data. Continue?",
        abort=True
    )
    
    # 2. 备份（如果需要）
    if backup:
        backup_db()
    
    # 3. 删除并重建
    drop_all_tables()
    run_script("scripts/init_db.py")
```

---

## 🛠️ 技术实现

### 依赖包

```python
# requirements-cli.txt
click>=8.1.0              # CLI 框架
jinja2>=3.1.0             # 模板引擎
colorama>=0.4.6           # 终端颜色（Windows）
rich>=13.0.0              # 美化输出
questionary>=2.0.0        # 交互式提示
```

### 项目结构

```
fastapi-scaffold/
├── cli/
│   ├── __init__.py
│   ├── main.py                 # CLI 入口
│   ├── commands/               # 命令实现
│   │   ├── __init__.py
│   │   ├── init.py             # init 命令
│   │   ├── generate.py         # generate 命令
│   │   ├── check.py            # check 命令
│   │   ├── db.py               # db 命令
│   │   └── admin.py            # admin 命令
│   │
│   ├── templates/              # Jinja2 模板
│   │   ├── model.py.j2
│   │   ├── schema.py.j2
│   │   ├── crud.py.j2
│   │   └── api.py.j2
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── file_ops.py         # 文件操作
│       ├── code_gen.py         # 代码生成
│       ├── validators.py       # 验证器
│       └── formatters.py       # 格式化器
│
├── setup.py                    # 安装配置
└── pyproject.toml              # 项目配置
```

### CLI 入口实现

```python
# cli/main.py
import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    FastAPI Scaffold - 企业级 FastAPI 脚手架工具
    
    快速初始化项目，自动生成代码，提升开发效率。
    """
    pass

# 注册命令
from cli.commands import init, generate, check, db, admin

cli.add_command(init.init)
cli.add_command(generate.generate)
cli.add_command(check.check)
cli.add_command(db.db)
cli.add_command(admin.admin)

if __name__ == '__main__':
    cli()
```

---

## 🎨 用户体验设计

### 交互式向导

```python
# 使用 questionary 实现交互
import questionary

def interactive_init():
    """交互式项目初始化"""
    console.print("[bold cyan]FastAPI Scaffold - 项目初始化向导[/]")
    
    # 1. 项目名称
    name = questionary.text(
        "项目名称:",
        validate=lambda x: len(x) > 0
    ).ask()
    
    # 2. 数据库选择
    db = questionary.select(
        "选择数据库:",
        choices=['SQLite (开发)', 'PostgreSQL (生产)']
    ).ask()
    
    # 3. 认证方式
    auth = questionary.select(
        "认证方式:",
        choices=['JWT (推荐)', 'OAuth2']
    ).ask()
    
    # 4. 权限模型
    rbac = questionary.select(
        "权限模型:",
        choices=['Casbin RBAC (推荐)', 'Simple']
    ).ask()
    
    # 5. 包含示例
    examples = questionary.confirm(
        "包含示例代码?",
        default=True
    ).ask()
    
    # 6. 确认创建
    console.print("\n[bold]配置总结:[/]")
    console.print(f"  项目名称: {name}")
    console.print(f"  数据库: {db}")
    console.print(f"  认证: {auth}")
    console.print(f"  权限: {rbac}")
    console.print(f"  示例: {'是' if examples else '否'}\n")
    
    if questionary.confirm("确认创建?").ask():
        init_project(name, db, auth, rbac, not examples)
```

### 进度显示

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

def init_project_with_progress(name, config):
    """带进度显示的项目初始化"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        
        task = progress.add_task("创建项目目录...", total=None)
        create_directory(name)
        
        progress.update(task, description="复制模板文件...")
        copy_template(name)
        
        progress.update(task, description="替换配置变量...")
        replace_variables(name, config)
        
        progress.update(task, description="初始化 Git 仓库...")
        init_git(name)
        
        progress.update(task, description="安装依赖...")
        install_dependencies(name)
    
    console.print("[bold green]✓[/] 项目创建成功!")
```

### 美化输出

```python
from rich.table import Table
from rich.panel import Panel

def print_next_steps(project_name):
    """打印下一步指引"""
    # 创建面板
    panel = Panel(
        f"""[bold cyan]项目创建成功！[/]

下一步:
  1. cd {project_name}
  2. python -m venv venv
  3. source venv/bin/activate  # Windows: venv\\Scripts\\activate
  4. pip install -r requirements.txt
  5. scaffold db init
  6. uvicorn app.main:app --reload

访问:
  - API 文档: http://localhost:8000/docs
  - 健康检查: http://localhost:8000/health

默认管理员:
  - 用户名: admin
  - 密码: admin123
        """,
        title="🎉 完成",
        border_style="green"
    )
    console.print(panel)
```

---

## 📚 配置文件

### scaffold.yaml

```yaml
# 项目配置文件（可选）
project:
  name: my-project
  version: 1.0.0
  description: My FastAPI project

database:
  type: sqlite
  url: sqlite:///./app.db

generation:
  # 代码生成默认配置
  model:
    add_created_at: true
    add_updated_at: true
    add_is_deleted: false
  
  schema:
    use_config_dict: true
    from_attributes: true
    extra: forbid
  
  api:
    add_auth: true
    add_pagination: true
    add_search: false

templates:
  # 自定义模板路径
  model: templates/custom_model.py.j2
  schema: templates/custom_schema.py.j2
```

---

## 🧪 测试计划

### 单元测试

```python
# tests/test_init_command.py
def test_init_creates_project():
    """测试 init 命令创建项目"""
    result = runner.invoke(cli, ['init', 'test-project'])
    assert result.exit_code == 0
    assert Path('test-project').exists()

def test_init_with_postgres():
    """测试使用 PostgreSQL 初始化"""
    result = runner.invoke(
        cli,
        ['init', 'test-project', '--db=postgres']
    )
    assert result.exit_code == 0
    # 验证数据库配置
    config = load_config('test-project/.env')
    assert 'postgresql' in config['DATABASE_URL']
```

### 集成测试

```python
# tests/test_full_workflow.py
def test_full_workflow():
    """测试完整工作流"""
    # 1. 初始化项目
    init_project('test-app')
    
    # 2. 生成 CRUD 模块
    generate_crud('article', fields='title:str,content:text')
    
    # 3. 生成 API
    generate_api('article', auth=True)
    
    # 4. 检查代码
    result = run_check(all=True)
    assert result.exit_code == 0
    
    # 5. 初始化数据库
    db_init()
    
    # 6. 验证应用可以启动
    assert can_start_app('test-app')
```

---

## 📖 使用示例

### 示例 1: 快速创建博客系统

```bash
# 1. 初始化项目
scaffold init my-blog

# 2. 生成文章模块
cd my-blog
scaffold generate crud article \
  --fields="title:str,content:text,author_id:int,published:bool" \
  --api --test

# 3. 生成评论模块
scaffold generate crud comment \
  --fields="article_id:int,user_id:int,content:text" \
  --api

# 4. 初始化数据库
scaffold db init

# 5. 启动服务
uvicorn app.main:app --reload
```

### 示例 2: 添加新功能模块

```bash
# 在现有项目中添加产品模块
scaffold generate crud product \
  --fields="name:str,price:float,stock:int,category_id:int" \
  --api --test

# 检查代码质量
scaffold check --all

# 生成数据库迁移
scaffold db migrate "add product table"
scaffold db upgrade
```

---

## 🔄 版本规划

### v1.0.0 (MVP)

```
✅ init 命令（基础功能）
✅ generate crud 命令
✅ generate api 命令
✅ check 命令（基础检查）
✅ db init 命令
```

### v1.1.0

```
⏳ 交互式向导
⏳ 进度显示
⏳ 配置文件支持
⏳ db migrate/upgrade 命令
⏳ add feature 命令
```

### v1.2.0

```
⏳ 自定义模板支持
⏳ 插件系统
⏳ Web UI
⏳ 项目模板市场
```

---

**维护者**: 项目团队  
**版本**: v1.0.0  
**创建日期**: 2026-01-01

---

*"Simple tools for complex tasks"*
