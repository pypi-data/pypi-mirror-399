# Jinja2 Templates

代码生成模板集合

---

## 📁 模板列表

### 1. model.py.j2 - Model 模板

**用途**: 生成 SQLAlchemy 2.0 Model 类

**变量**:
- `module_name`: 模块名（如 article）
- `class_name`: 类名（如 Article）
- `table_name`: 表名（如 articles）
- `fields`: 字段列表
  - `name`: 字段名
  - `type`: 字段类型
  - `required`: 是否必需
  - `sa_type`: SQLAlchemy 类型
  - `type_hint`: Python 类型提示
- `has_date`: 是否需要导入 date

**生成内容**:
- SQLAlchemy Base 类继承
- Mapped 类型定义
- 主键（id）
- 业务字段
- 审计字段（created_at, updated_at）
- 表配置（sqlite_autoincrement）

**示例**:
```python
class Article(Base):
    __tablename__ = "articles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

---

### 2. schema.py.j2 - Schema 模板

**用途**: 生成 Pydantic Schema 类（Base/Create/Update/Response）

**变量**:
- `module_name`: 模块名
- `class_name`: 类名
- `fields`: 字段列表
  - `name`: 字段名
  - `type`: 字段类型
  - `required`: 是否必需
  - `type_hint`: Python 类型提示
  - `base_type`: 基础类型（不含 Optional）
  - `pydantic_field`: Pydantic Field 定义
- `has_date`: 是否需要导入 date

**生成内容**:
- Base Schema（共享字段）
- Create Schema（继承 Base）
- Update Schema（所有字段可选）
- Response Schema（包含 id 和审计字段）

**示例**:
```python
class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)

class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

---

### 3. crud.py.j2 - CRUD 模板

**用途**: 生成 CRUD 操作类

**变量**:
- `module_name`: 模块名
- `class_name`: 类名

**生成内容**:
- CRUD 类定义
- get_list(): 分页列表
- get_by_id(): 根据 ID 查询
- create(): 创建
- update(): 更新
- delete(): 删除
- 实例化 CRUD 对象

**示例**:
```python
class ArticleCRUD:
    def get_list(self, db: Session, skip: int = 0, limit: int = 20):
        query = db.query(Article)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def create(self, db: Session, obj_in: ArticleCreate):
        db_obj = Article(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        return db_obj

article_crud = ArticleCRUD()
```

---

### 4. api.py.j2 - API 模板

**用途**: 生成 FastAPI 路由

**变量**:
- `module_name`: 模块名
- `class_name`: 类名
- `api_prefix`: API 路径前缀
- `api_tag`: OpenAPI 标签
- `auth`: 是否需要认证

**生成内容**:
- APIRouter 定义
- 5 个 RESTful 端点：
  - GET /<module>s - 列表（分页）
  - POST /<module>s - 创建
  - GET /<module>s/{id} - 详情
  - PUT /<module>s/{id} - 更新
  - DELETE /<module>s/{id} - 删除
- 认证依赖（可选）
- 错误处理（404）

**示例**:
```python
router = APIRouter(prefix="/api/v1/articles", tags=["Article管理"])

@router.get("", response_model=PaginatedResponse[ArticleResponse])
def list_articles(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * page_size
    items, total = article_crud.get_list(db, skip=skip, limit=page_size)
    return PaginatedResponse(items=items, total=total, ...)
```

---

## 🎨 模板语法

### 变量引用

```jinja2
{{ module_name }}      # 输出变量
{{ class_name|title }} # 使用过滤器
```

### 条件判断

```jinja2
{% if auth %}
from app.core.dependencies import get_current_user
{% endif %}
```

### 循环

```jinja2
{% for field in fields %}
{{ field.name }}: Mapped[{{ field.type_hint }}]
{% endfor %}
```

### 去除空白

```jinja2
{%- for field in fields %}   # 去除前面空白
{{ field.name }}
{%- endfor %}                 # 去除后面空白
```

---

## 🔧 字段类型映射

### Python 类型 → SQLAlchemy 类型

```python
TYPE_MAPPING = {
    'str': 'String(255)',
    'text': 'Text',
    'int': 'Integer',
    'float': 'Float',
    'bool': 'Boolean',
    'date': 'Date',
    'datetime': 'DateTime',
    'json': 'JSON',
    'email': 'String(100)',
    'url': 'String(500)',
    'phone': 'String(20)',
}
```

### Python 类型 → Pydantic Field

```python
FIELD_CONFIGS = {
    'str': '..., min_length=1, max_length=255',
    'text': '..., min_length=1',
    'int': '..., ge=0',
    'float': '..., ge=0.0',
    'bool': '...',
    'email': '..., max_length=100',
    'phone': '..., pattern=r"^1[3-9]\\d{9}$"',
}
```

---

## 📝 模板开发指南

### 添加新模板

1. 创建 `.j2` 文件在 `cli/templates/` 目录
2. 定义模板变量
3. 在 `cli/utils/code_gen.py` 添加生成函数
4. 在命令中调用生成函数

**示例**: 添加测试模板

```jinja2
{# test.py.j2 #}
"""{{ class_name }} Tests"""
import pytest
from app.models.{{ module_name }} import {{ class_name }}

def test_create_{{ module_name }}():
    """测试创建{{ class_name }}"""
    # TODO: 实现测试
    pass
```

```python
# cli/utils/code_gen.py
def generate_test(module_name: str, class_name: str) -> str:
    context = {
        'module_name': module_name,
        'class_name': class_name,
    }
    return render_template('test.py.j2', context)
```

### 模板最佳实践

1. **保持简洁**: 模板应该清晰易读
2. **注释说明**: 复杂逻辑添加注释
3. **缩进一致**: 使用 4 空格缩进
4. **去除空白**: 使用 `{%-` 和 `-%}` 控制空白
5. **类型安全**: 生成的代码应该类型安全
6. **遵循规范**: 符合项目代码规范

### 测试模板

```bash
# 1. 生成测试项目
python cli/main.py init test-template

# 2. 生成代码
cd test-template
python ../cli/main.py generate crud article --fields="title:str,content:text"

# 3. 验证生成的代码
python -c "from app.models.article import Article; print('OK')"
python -c "from app.schemas.article import ArticleResponse; print('OK')"

# 4. 类型检查
python -m mypy app/models/article.py
python -m mypy app/schemas/article.py

# 5. 清理
cd ..
rm -rf test-template
```

---

## 🎯 模板变量参考

### 通用变量

```python
module_name: str      # 模块名（小写，下划线）
class_name: str       # 类名（PascalCase）
table_name: str       # 表名（复数形式）
```

### 字段变量

```python
field = {
    'name': str,           # 字段名
    'type': str,           # 原始类型（str/int/...）
    'required': bool,      # 是否必需
    'sa_type': str,        # SQLAlchemy 类型
    'type_hint': str,      # Python 类型提示（含 Optional）
    'base_type': str,      # 基础类型（不含 Optional）
    'pydantic_field': str, # Pydantic Field 定义
}
```

### API 变量

```python
api_prefix: str       # API 路径前缀
api_tag: str          # OpenAPI 标签
auth: bool            # 是否需要认证
```

---

## 🔍 调试技巧

### 查看生成的代码

```python
# 在 cli/utils/code_gen.py 中添加调试输出
def generate_model(module_name, class_name, fields):
    code = render_template('model.py.j2', context)
    print(code)  # 调试输出
    return code
```

### 验证模板语法

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('cli/templates'))
template = env.get_template('model.py.j2')

# 测试渲染
context = {'module_name': 'test', 'class_name': 'Test', ...}
result = template.render(**context)
print(result)
```

---

## 📚 参考资源

- [Jinja2 官方文档](https://jinja.palletsprojects.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

**维护者**: 项目团队  
**版本**: v1.0.0  
**更新日期**: 2026-01-01
