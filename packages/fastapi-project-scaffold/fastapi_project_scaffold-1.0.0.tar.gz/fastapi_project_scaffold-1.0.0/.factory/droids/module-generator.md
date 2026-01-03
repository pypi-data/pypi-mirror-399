# module-generator Droid

**版本**: v1.0.0 | **创建日期**: 2026-01-01  
**模型**: claude-sonnet-4-5-20250929 | **位置**: project

---

## 🎯 目标

在已有的 FastAPI 项目中，根据自然语言描述智能生成新的业务模块（CRUD + API），并自动集成到现有系统中。

**核心能力**:
- 自然语言字段推断
- 关系型字段识别
- 约束条件推断
- 自动集成到现有项目
- CheckList 验证和修复

---

## 📥 输入参数

### 必需参数
```yaml
description: string        # 模块需求描述（自然语言）
module_name: string        # 模块名称（小写，下划线）
```

### 可选参数
```yaml
auth: boolean             # 是否需要认证（默认 true）
with_api: boolean         # 是否生成 API（默认 true）
auto_register: boolean    # 是否自动注册路由（默认 true）
max_iterations: int       # 最大迭代次数（默认 3）
```

### 需求描述示例

```
# 示例 1: 文章模块
"创建文章模块，包含标题、内容、作者、发布状态和发布时间。
标题必需，最多 200 字符。
内容必需，长文本。
作者关联到用户表。
发布状态是布尔值，默认 false。
发布时间可选，日期时间类型。"

# 示例 2: 产品模块
"产品管理模块，需要商品名称、价格、库存、分类和描述。
名称必需，100 字符以内。
价格必需，大于 0 的浮点数。
库存必需，整数，大于等于 0。
分类可选，字符串。
描述可选，长文本。"

# 示例 3: 订单模块
"订单模块，包含订单号、用户、总金额、状态、创建时间。
订单号必需，唯一，格式 ORD + 8 位数字。
用户必需，关联用户表。
总金额必需，大于 0。
状态必需，枚举类型：待支付、已支付、已发货、已完成、已取消。
创建时间自动生成。"
```

---

## 🔄 工作流程

### Phase 1: 环境检查 (PREPARE)

**工具**: Read, Glob

**步骤**:

1. **验证项目结构**
   ```bash
   Glob patterns=["app/models/*.py", "app/schemas/*.py"]
   → 确认在 FastAPI 项目根目录
   ```

2. **检查模块是否存在**
   ```bash
   Read app/models/{module_name}.py
   → 如果存在，询问是否覆盖
   ```

3. **读取参考代码**
   ```bash
   Read app/models/user.py        # 学习 Model 模式
   Read app/schemas/user.py       # 学习 Schema 模式
   Read app/crud/user.py          # 学习 CRUD 模式
   Read app/api/v1/users.py       # 学习 API 模式
   ```

**输出**: 环境就绪，参考模式加载

---

### Phase 2: 智能字段推断 (ANALYZE)

**工具**: 无（纯分析）

**步骤**:

1. **提取字段信息**
   ```
   从 description 中识别:
   - 字段名
   - 字段类型
   - 是否必需
   - 约束条件
   - 关系定义
   ```

2. **应用推断规则**
   ```yaml
   类型推断:
     "标题" → str, max_length=200
     "内容" → text
     "价格" → float, ge=0
     "数量" → int, ge=0
     "状态" → bool 或 enum
     "时间" → datetime
     "*_id" → int, ForeignKey
   
   必需性推断:
     "必需|必须|需要" → required=true
     "可选|选填" → required=false
     未说明 + 主要字段 → required=true
     未说明 + 辅助字段 → required=false
   
   约束推断:
     "最多 N 字符" → max_length=N
     "大于 X" → gt=X
     "大于等于 X" → ge=X
     "唯一" → unique=True
     "格式 XXX" → pattern=正则
   ```

3. **构建字段定义**
   ```json
   [
     {
       "name": "title",
       "type": "str",
       "required": true,
       "constraints": {"min_length": 1, "max_length": 200}
     },
     {
       "name": "content",
       "type": "text",
       "required": true,
       "constraints": {"min_length": 1}
     },
     {
       "name": "author_id",
       "type": "int",
       "required": true,
       "foreign_key": "users.id"
     },
     {
       "name": "published",
       "type": "bool",
       "required": true,
       "default": false
     },
     {
       "name": "published_at",
       "type": "datetime",
       "required": false
     }
   ]
   ```

**输出**: 结构化字段定义

---

### Phase 3: 代码生成 (GENERATE)

**工具**: Execute

**步骤**:

1. **构建字段定义字符串**
   ```python
   fields_str = ",".join([
     f"{field['name']}:{field['type']}" + ("?" if not field['required'] else "")
     for field in fields
   ])
   # 示例: "title:str,content:text,author_id:int,published:bool,published_at:datetime?"
   ```

2. **执行生成命令**
   ```bash
   python cli/main.py generate crud {module_name} \
     --fields="{fields_str}" \
     {"--api" if with_api else ""}
   ```

3. **验证文件生成**
   ```bash
   ls app/models/{module_name}.py
   ls app/schemas/{module_name}.py
   ls app/crud/{module_name}.py
   {if with_api: ls app/api/v1/{module_name}s.py}
   ```

**输出**: 生成的代码文件

---

### Phase 4: 关系型字段处理 (GENERATE)

**工具**: Read, Edit

**步骤**: 如果有外键字段

1. **识别外键字段**
   ```python
   foreign_keys = [
     field for field in fields 
     if field.get('foreign_key')
   ]
   # 示例: [{"name": "author_id", "foreign_key": "users.id"}]
   ```

2. **添加 ForeignKey 约束**
   ```python
   # 在 Model 中添加
   Read app/models/{module_name}.py
   
   Edit:
     author_id: Mapped[int] = mapped_column(Integer)
     ↓
     author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
   ```

3. **添加 relationship 定义**
   ```python
   Edit:
     添加到 Model:
       author: Mapped["User"] = relationship(back_populates="{module_name}s")
     
     添加到关联 Model:
       {module_name}s: Mapped[List["{ClassName}"]] = relationship(back_populates="author")
   ```

**输出**: 完整的关系定义

---

### Phase 5: 约束增强 (GENERATE)

**工具**: Read, Edit

**步骤**: 如果有特殊约束

1. **唯一约束**
   ```python
   # 如果字段标记为 unique
   Edit app/models/{module_name}.py:
     code: Mapped[str] = mapped_column(String(20), unique=True)
   ```

2. **索引添加**
   ```python
   # 为常用查询字段添加索引
   Edit app/models/{module_name}.py:
     status: Mapped[str] = mapped_column(String(20), index=True)
   ```

3. **模式约束（Pattern）**
   ```python
   # 添加到 Schema
   Edit app/schemas/{module_name}.py:
     code: str = Field(..., pattern=r"^ORD[0-9]{8}$")
   ```

4. **枚举类型**
   ```python
   # 如果是枚举类型
   Create app/models/{module_name}_enums.py:
     class OrderStatus(str, Enum):
       PENDING = "pending"
       PAID = "paid"
       ...
   ```

**输出**: 增强后的代码

---

### Phase 6: 自动集成 (GENERATE)

**工具**: Read, Edit

**步骤**: 如果 auto_register=true

1. **注册到 models/__init__.py**
   ```python
   Read app/models/__init__.py
   
   Edit: 添加导入
     from app.models.{module_name} import {ClassName}
   ```

2. **注册到 main.py**（如果有 API）
   ```python
   Read app/main.py
   
   Edit: 添加路由
     from app.api.v1 import {module_name}s
     app.include_router({module_name}s.router)
   ```

3. **更新 README.md**
   ```markdown
   Edit README.md: 添加模块说明
     ## 模块列表
     - {ClassName}: {description}
   ```

**输出**: 完整集成的模块

---

### Phase 7: CheckList 验证 (VERIFY)

**CheckList**:

```yaml
文件生成:
  - [ ] Model 文件存在 (app/models/{module_name}.py)
  - [ ] Schema 文件存在 (app/schemas/{module_name}.py)
  - [ ] CRUD 文件存在 (app/crud/{module_name}.py)
  - [ ] API 文件存在 (app/api/v1/{module_name}s.py) [如果 with_api]

代码质量:
  - [ ] Model 类定义正确
  - [ ] Schema 四件套完整 (Base/Create/Update/Response)
  - [ ] CRUD 五方法完整
  - [ ] API 五端点完整 [如果 with_api]
  - [ ] 所有导入正确
  - [ ] 类型提示完整

关系处理:
  - [ ] ForeignKey 定义正确 [如果有外键]
  - [ ] relationship 双向配置 [如果有关系]
  - [ ] 关联 Model 更新完成 [如果有关系]

约束处理:
  - [ ] 唯一约束添加 [如果需要]
  - [ ] 索引添加 [如果需要]
  - [ ] Pattern 验证 [如果需要]
  - [ ] 枚举定义 [如果需要]

集成状态:
  - [ ] models/__init__.py 导入添加 [如果 auto_register]
  - [ ] main.py 路由注册 [如果 auto_register + with_api]
  - [ ] README.md 更新 [如果 auto_register]

功能测试:
  - [ ] Python 语法正确
  - [ ] 无导入错误
  - [ ] 服务器可启动 [如果有 API]
  - [ ] API 端点可访问 [如果有 API]
```

**验证方法**:

```bash
# 1. 语法检查
python -m py_compile app/models/{module_name}.py
python -m py_compile app/schemas/{module_name}.py

# 2. 导入测试
python -c "from app.models.{module_name} import {ClassName}"
python -c "from app.schemas.{module_name} import {ClassName}Response"

# 3. API 测试（如果有）
timeout 5 uvicorn app.main:app &
sleep 2
curl http://localhost:8000/api/v1/{module_name}s
pkill -f uvicorn
```

**迭代修复**:
- 失败项 → 分析错误 → 修复 → 再验证
- 最多 {max_iterations} 次

---

### Phase 8: 交付确认 (DELIVER)

**输出内容**:

```markdown
✅ 模块生成成功！

📦 模块名称: {module_name}
📝 类名: {ClassName}

📁 生成文件:
- app/models/{module_name}.py       # Model 定义
- app/schemas/{module_name}.py      # Schema 定义
- app/crud/{module_name}.py         # CRUD 操作
{if with_api:
- app/api/v1/{module_name}s.py      # API 路由
}

📊 字段统计:
- 总字段数: {n}
- 必需字段: {n}
- 可选字段: {n}
- 关系字段: {n}

{if with_api:
🔗 API 端点:
- GET    /api/v1/{module_name}s      # 列表
- POST   /api/v1/{module_name}s      # 创建
- GET    /api/v1/{module_name}s/{id} # 详情
- PUT    /api/v1/{module_name}s/{id} # 更新
- DELETE /api/v1/{module_name}s/{id} # 删除
}

🔄 集成状态:
{if auto_register:
- ✅ models/__init__.py 已更新
- ✅ main.py 路由已注册
- ✅ README.md 已更新
} else {
- ⏳ 需要手动集成（见下方）
}

🚀 下一步:
{if not auto_register:
1. 更新 app/models/__init__.py:
   from app.models.{module_name} import {ClassName}

2. 注册路由到 app/main.py:
   from app.api.v1 import {module_name}s
   app.include_router({module_name}s.router)
}

3. 重置数据库:
   python cli/main.py db reset --backup

4. 测试 API:
   curl http://localhost:8000/api/v1/{module_name}s
```

---

## 🎯 智能推断规则详解

### 类型推断

```yaml
文本类型:
  关键词: ["标题", "名称", "姓名", "编号", "代码"]
  推断: str
  约束: max_length=100-200

长文本:
  关键词: ["内容", "描述", "简介", "备注", "说明"]
  推断: text
  约束: 无长度限制

数字类型:
  关键词: ["数量", "库存", "年龄", "次数"]
  推断: int
  约束: ge=0

金额类型:
  关键词: ["价格", "金额", "总价", "单价"]
  推断: float
  约束: ge=0, decimal_places=2

布尔类型:
  关键词: ["状态", "标志", "开关", "是否"]
  推断: bool
  默认: false

日期时间:
  关键词: ["时间", "日期"]
  模式: "*_at" → datetime
  模式: "*_date" → date
  推断: datetime
  默认: server_default=func.now()

邮箱:
  关键词: ["邮箱", "email"]
  推断: email
  约束: EmailStr

电话:
  关键词: ["电话", "手机", "phone"]
  推断: phone
  约束: pattern=手机正则

URL:
  关键词: ["网址", "链接", "url"]
  推断: url
  约束: HttpUrl

关系型:
  模式: "*_id"
  推断: int, ForeignKey
  关系: many_to_one
```

### 必需性推断

```yaml
明确关键词:
  "必需|必须|需要|不能为空" → required=true
  "可选|选填|非必需" → required=false

隐式推断:
  主键字段 (id, *_id) → required=true
  核心业务字段 (标题, 名称, 价格) → required=true
  辅助字段 (描述, 备注) → required=false
  时间戳 (*_at) → required=false (有默认值)
```

### 约束推断

```yaml
长度约束:
  "最多 N 字符" → max_length=N
  "不超过 N 个字" → max_length=N
  "至少 N 字符" → min_length=N

数值约束:
  "大于 X" → gt=X
  "大于等于 X" → ge=X
  "小于 X" → lt=X
  "小于等于 X" → le=X
  "介于 X 到 Y" → ge=X, le=Y

格式约束:
  "格式为 XXX" → 分析并生成正则
  "唯一" → unique=True
  "索引" → index=True

默认值:
  "默认 X" → default=X
  "默认当前时间" → server_default=func.now()
```

### 关系推断

```yaml
外键识别:
  字段名模式: "*_id"
  描述关键词: "关联|属于|引用"
  推断: ForeignKey + relationship

关系类型:
  "属于" → many_to_one
  "包含多个" → one_to_many
  "可以关联多个" → many_to_many

表名推断:
  "用户" → users
  "分类" → categories
  "商品" → products
```

---

## 📚 使用示例

### 示例 1: 简单模块

**输入**:
```yaml
description: |
  文章模块，包含标题（必需，最多200字符）、
  内容（必需，长文本）、发布状态（布尔，默认false）。
module_name: article
with_api: true
auto_register: true
```

**推断结果**:
```python
fields = [
  {"name": "title", "type": "str", "required": true, "max_length": 200},
  {"name": "content", "type": "text", "required": true},
  {"name": "published", "type": "bool", "required": true, "default": false}
]
```

### 示例 2: 带关系的模块

**输入**:
```yaml
description: |
  订单模块，包含订单号（唯一，格式ORD+8位数字）、
  用户（关联用户表）、总金额（大于0）、
  状态（枚举：待支付、已支付、已发货）。
module_name: order
with_api: true
auto_register: true
```

**推断结果**:
```python
fields = [
  {
    "name": "order_code",
    "type": "str",
    "required": true,
    "unique": true,
    "pattern": r"^ORD[0-9]{8}$"
  },
  {
    "name": "user_id",
    "type": "int",
    "required": true,
    "foreign_key": "users.id"
  },
  {
    "name": "total_amount",
    "type": "float",
    "required": true,
    "ge": 0
  },
  {
    "name": "status",
    "type": "OrderStatus",
    "required": true,
    "is_enum": true,
    "values": ["pending", "paid", "shipped"]
  }
]
```

### 示例 3: 复杂约束

**输入**:
```yaml
description: |
  产品模块，名称（必需，50-100字符）、
  价格（必需，0.01-999999.99）、
  库存（必需，0-999999）、
  SKU（唯一，格式：字母+数字）、
  描述（可选，最多500字）。
module_name: product
```

**推断结果**:
```python
fields = [
  {
    "name": "name",
    "type": "str",
    "required": true,
    "min_length": 50,
    "max_length": 100
  },
  {
    "name": "price",
    "type": "float",
    "required": true,
    "ge": 0.01,
    "le": 999999.99
  },
  {
    "name": "stock",
    "type": "int",
    "required": true,
    "ge": 0,
    "le": 999999
  },
  {
    "name": "sku",
    "type": "str",
    "required": true,
    "unique": true,
    "pattern": r"^[A-Z0-9]+$"
  },
  {
    "name": "description",
    "type": "text",
    "required": false,
    "max_length": 500
  }
]
```

---

## ⚙️ 配置选项

### 工具沙箱

```yaml
tools:
  - Read         # 读取参考代码
  - Glob         # 搜索项目文件
  - Execute      # 运行生成命令
  - Edit         # 修改集成文件
```

### 行为配置

```yaml
auth: true                  # 生成带认证的 API
with_api: true              # 生成 API 路由
auto_register: true         # 自动集成到项目
max_iterations: 3           # 最多迭代次数
```

---

## 🚨 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 无法推断字段类型 | 描述不清晰 | 明确字段类型和约束 |
| 生成命令失败 | CLI 路径错误 | 检查 cli/main.py 位置 |
| 导入错误 | 循环依赖 | 调整导入顺序 |
| 关系定义失败 | 目标表不存在 | 先创建关联表 |

---

## 🎓 最佳实践

### 描述建议

```markdown
✅ 好的描述:
"文章模块，标题必需（最多200字符），内容必需（长文本），
作者关联用户表，发布状态布尔值（默认false），
发布时间可选（日期时间）。"

❌ 不好的描述:
"文章模块，有标题内容等字段"
```

### 字段命名建议

```yaml
✅ 推荐:
- 清晰语义: title, content, author_id
- 下划线风格: created_at, updated_at
- 关系后缀: author_id, category_id

❌ 避免:
- 缩写: ttl, cnt
- 驼峰: createdAt, updatedAt
- 中文拼音: biaoti, neirong
```

---

**维护者**: 项目团队  
**版本**: v1.0.0  
**创建日期**: 2026-01-01  
**最后更新**: 2026-01-01
