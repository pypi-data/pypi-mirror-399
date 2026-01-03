# scaffold-generator Droid

**版本**: v1.0.0 | **创建日期**: 2026-01-01  
**模型**: claude-sonnet-4-5-20250929 | **位置**: project

---

## 🎯 目标

根据用户需求描述，智能生成完整的 FastAPI 项目脚手架，包括数据模型、API 路由、CRUD 操作等。

**核心能力**:
- 自然语言需求分析
- 智能字段推断
- 关系型字段识别
- 完整项目生成
- CheckList 验证

---

## 📥 输入参数

### 必需参数
```yaml
description: string        # 项目需求描述（自然语言）
project_name: string       # 项目名称（小写，下划线或中划线）
```

### 可选参数
```yaml
database: string           # 数据库类型（sqlite|postgres，默认 sqlite）
auth: boolean             # 是否需要认证（默认 true）
include_examples: boolean # 是否包含示例代码（默认 false）
max_iterations: int       # 最大迭代次数（默认 3）
```

### 需求描述示例

```
# 示例 1: 博客系统
"创建一个博客系统，包含文章、评论和标签。
文章有标题、内容、作者、发布状态和发布时间。
评论关联到文章，包含内容、作者和创建时间。
标签可以关联多篇文章。"

# 示例 2: 电商后台
"开发一个电商后台，需要商品管理、订单管理和库存管理。
商品包含名称、价格、库存、分类和描述。
订单包含订单号、商品、数量、总价和状态。
库存记录包含商品、仓库、数量和更新时间。"

# 示例 3: 任务管理
"任务管理应用，支持任务列表和任务项。
任务列表有名称和描述。
任务项属于某个列表，包含标题、描述、优先级、状态和截止日期。"
```

---

## 🔄 工作流程

### Phase 1: 需求分析 (ANALYZE)

**工具**: Read, Grep

**步骤**:

1. **读取参考模板**
   ```
   Read fastapi-scaffold/template/app/models/*.py
   Read fastapi-scaffold/template/app/schemas/*.py
   → 学习现有代码模式和规范
   ```

2. **解析需求描述**
   ```
   从 description 中提取:
   - 实体列表（Entity List）
   - 字段定义（Field Definitions）
   - 关系类型（Relationships）
   - 业务规则（Business Rules）
   ```

3. **构建实体模型**
   ```json
   [
     {
       "name": "Article",
       "table": "articles",
       "fields": [
         {"name": "title", "type": "str", "required": true},
         {"name": "content", "type": "text", "required": true},
         {"name": "author_id", "type": "int", "required": true},
         {"name": "published", "type": "bool", "required": true},
         {"name": "published_at", "type": "datetime", "required": false}
       ],
       "relationships": [
         {"type": "many_to_one", "target": "User", "field": "author"}
       ]
     }
   ]
   ```

**输出**: 结构化实体定义列表

---

### Phase 2: 项目初始化 (GENERATE)

**工具**: Execute

**步骤**:

1. **运行 CLI 初始化命令**
   ```bash
   cd fastapi-scaffold
   python cli/main.py init {project_name} \
     --db={database} \
     {"--no-examples" if not include_examples}
   ```

2. **验证项目创建**
   ```bash
   cd {project_name}
   ls -la app/
   # 确认目录结构正确
   ```

**输出**: 初始化的项目目录

---

### Phase 3: 模块生成 (GENERATE)

**工具**: Execute

**步骤**: 对每个实体执行

1. **生成字段定义字符串**
   ```python
   fields_str = ",".join([
     f"{field['name']}:{field['type']}" + ("?" if not field['required'] else "")
     for field in entity['fields']
   ])
   # 示例: "title:str,content:text,published:bool?"
   ```

2. **执行 CRUD 生成命令**
   ```bash
   cd {project_name}
   python ../cli/main.py generate crud {entity_name} \
     --fields="{fields_str}" \
     --api
   ```

3. **处理关系型字段**（如果有）
   ```
   - 识别 *_id 字段
   - 添加 ForeignKey 约束
   - 添加 relationship 定义
   - 生成关联 API（可选）
   ```

**输出**: 所有实体的 Model/Schema/CRUD/API 文件

---

### Phase 4: 集成配置 (GENERATE)

**工具**: Edit

**步骤**:

1. **注册路由到 main.py**
   ```python
   # 在 app/main.py 中添加
   from app.api.v1 import articles, comments, tags
   
   app.include_router(articles.router)
   app.include_router(comments.router)
   app.include_router(tags.router)
   ```

2. **更新 models/__init__.py**
   ```python
   from app.models.article import Article
   from app.models.comment import Comment
   from app.models.tag import Tag
   ```

3. **创建 README.md**
   ```markdown
   # {Project Name}
   
   ## 实体列表
   - Article: 文章管理
   - Comment: 评论管理
   - Tag: 标签管理
   
   ## API 端点
   - GET/POST /api/v1/articles
   - GET/POST /api/v1/comments
   - GET/POST /api/v1/tags
   ```

**输出**: 完整集成的项目

---

### Phase 5: 数据库初始化 (GENERATE)

**工具**: Execute

**步骤**:

1. **初始化数据库**
   ```bash
   cd {project_name}
   python ../cli/main.py db init
   ```

2. **验证表创建**
   ```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('app.db')
   tables = conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()
   print('Tables:', tables)
   "
   ```

**输出**: 数据库文件和表结构

---

### Phase 6: CheckList 验证 (VERIFY)

**CheckList**:

```yaml
项目结构:
  - [ ] 项目目录创建成功
  - [ ] app/ 目录结构完整
  - [ ] .env 文件存在

代码生成:
  - [ ] 所有实体的 Model 文件存在
  - [ ] 所有实体的 Schema 文件存在
  - [ ] 所有实体的 CRUD 文件存在
  - [ ] 所有实体的 API 文件存在

集成配置:
  - [ ] main.py 路由注册完成
  - [ ] models/__init__.py 导入完成
  - [ ] README.md 创建完成

数据库:
  - [ ] 数据库文件创建成功
  - [ ] 所有表创建成功
  - [ ] 表字段匹配定义

代码质量:
  - [ ] 所有 Python 文件语法正确
  - [ ] 没有导入错误
  - [ ] 类型提示完整

功能测试:
  - [ ] 服务器可以启动
  - [ ] OpenAPI 文档可访问
  - [ ] API 端点正常响应
```

**验证方法**:

```bash
# 1. 语法检查
python -m py_compile app/**/*.py

# 2. 导入测试
python -c "from app.main import app; print('OK')"

# 3. 启动测试
timeout 5 uvicorn app.main:app &
sleep 2
curl http://localhost:8000/docs
pkill -f uvicorn
```

**迭代修复**:
- 如果验证失败，分析错误信息
- 修复相关文件
- 重新验证
- 最多迭代 {max_iterations} 次

---

### Phase 7: 交付确认 (DELIVER)

**输出内容**:

```markdown
✅ 项目生成成功！

📁 项目结构:
{project_name}/
├── app/
│   ├── models/         # {n} 个实体
│   ├── schemas/        # {n} 个实体
│   ├── crud/          # {n} 个实体
│   ├── api/v1/        # {n} 个路由
│   └── main.py        # 已注册路由
├── .env               # 环境配置
├── app.db             # 数据库（已初始化）
└── README.md          # 项目说明

📊 生成统计:
- 实体数: {n}
- API 端点: {n * 5}
- 数据表: {n}
- 代码文件: {n * 4 + 1}

🚀 快速开始:
cd {project_name}
uvicorn app.main:app --reload

📖 API 文档:
http://localhost:8000/docs

🔗 生成的 API:
{list_of_api_endpoints}
```

---

## 🎯 智能推断规则

### 字段类型推断

```yaml
关键词匹配:
  - "标题|名称|姓名" → str
  - "内容|描述|简介|备注" → text
  - "数量|库存|年龄" → int
  - "价格|金额|总价" → float
  - "状态|标志|开关" → bool（或 Enum）
  - "时间|日期" → datetime/date
  - "邮箱|email" → email
  - "电话|手机" → phone
  - "网址|链接" → url

业务规则:
  - "*_id" → int (ForeignKey)
  - "*_at" → datetime
  - "*_date" → date
  - "*_count" → int
  - "*_amount|*_price" → float
  - "*_status" → enum
```

### 关系推断

```yaml
关键词识别:
  - "属于|关联到" → many_to_one
  - "包含多个" → one_to_many
  - "可以关联多个" → many_to_many

字段名推断:
  - "author_id" → many_to_one(User, author)
  - "category_id" → many_to_one(Category, category)
  - "user_id" → many_to_one(User, user)
```

### 约束推断

```yaml
字符串:
  - 标题: max_length=200
  - 名称: max_length=100
  - 内容: max_length=无限制
  - 编号: pattern=正则

数字:
  - 价格: ge=0, le=999999.99
  - 数量: ge=0, le=999999
  - 年龄: ge=0, le=150

必需性:
  - 主要属性: required=true
  - 描述/备注: required=false
  - 时间戳: required=false（有默认值）
```

---

## 📚 使用示例

### 示例 1: 博客系统

**输入**:
```yaml
description: |
  创建一个博客系统，包含文章和评论。
  文章有标题、内容、作者、发布状态。
  评论关联到文章，包含内容和作者。
project_name: my-blog
database: sqlite
auth: true
```

**生成结果**:
```
✅ 2 个实体: Article, Comment
✅ 10 个 API 端点
✅ 2 张数据表
✅ 9 个代码文件
```

### 示例 2: 任务管理

**输入**:
```yaml
description: |
  任务管理应用，有任务列表和任务项。
  任务列表包含名称和描述。
  任务项属于列表，有标题、状态、优先级和截止日期。
project_name: task-manager
database: sqlite
auth: true
```

**生成结果**:
```
✅ 2 个实体: TaskList, TaskItem
✅ 10 个 API 端点
✅ 1 个关系: TaskItem.list_id → TaskList
✅ 2 张数据表
✅ 9 个代码文件
```

---

## ⚙️ 配置选项

### 工具沙箱

```yaml
tools:
  - Read         # 读取模板和参考
  - Grep         # 搜索代码模式
  - Execute      # 运行 CLI 命令
  - Edit         # 修改集成文件
```

### 迭代配置

```yaml
max_iterations: 3           # 最多迭代 3 次
verify_on_each_entity: true # 每个实体生成后验证
auto_fix: true              # 自动修复错误
```

---

## 🎓 最佳实践

### 需求描述建议

```markdown
✅ 好的描述:
"创建博客系统，包含文章、评论、标签三个模块。
文章有标题（必需）、内容（必需）、作者（关联用户）、发布状态（布尔）。
评论关联到文章，包含内容、作者、创建时间。
标签可以关联多篇文章（多对多关系）。"

❌ 不好的描述:
"做个博客"
```

### 实体命名建议

```yaml
✅ 推荐:
- 单数名词: Article, Comment, Tag
- PascalCase: TaskList, OrderItem
- 清晰语义: TrainingPlan, QuestionBank

❌ 避免:
- 复数: Articles (会自动转单数)
- 缩写: Art, Comm
- 动词: CreateArticle
```

---

## 🔍 调试模式

### 详细输出

```yaml
verbose: true  # 输出详细日志

日志内容:
- 需求解析结果
- 实体定义 JSON
- 执行的命令
- 验证结果
- 修复操作
```

### 暂停点

```yaml
pause_after_analyze: true   # 分析后暂停，供用户确认
pause_after_generate: true  # 生成后暂停，供用户检查
```

---

## 📊 输出格式

### 成功输出

```json
{
  "status": "success",
  "project_name": "my-blog",
  "entities": [
    {"name": "Article", "files": 4, "endpoints": 5},
    {"name": "Comment", "files": 4, "endpoints": 5}
  ],
  "total_files": 9,
  "total_endpoints": 10,
  "database_tables": 2,
  "next_steps": [
    "cd my-blog",
    "uvicorn app.main:app --reload",
    "open http://localhost:8000/docs"
  ]
}
```

### 失败输出

```json
{
  "status": "failed",
  "error": "Entity parsing failed",
  "details": "无法从描述中提取实体信息",
  "suggestion": "请提供更详细的实体和字段描述"
}
```

---

## 🚨 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 无法解析实体 | 描述太模糊 | 提供更详细的实体列表 |
| CLI 命令失败 | 模板路径错误 | 检查 fastapi-scaffold 目录 |
| 导入错误 | 循环依赖 | 调整实体导入顺序 |
| 数据库初始化失败 | 表定义冲突 | 检查字段名是否为 SQL 关键字 |

---

**维护者**: 项目团队  
**版本**: v1.0.0  
**创建日期**: 2026-01-01  
**最后更新**: 2026-01-01
