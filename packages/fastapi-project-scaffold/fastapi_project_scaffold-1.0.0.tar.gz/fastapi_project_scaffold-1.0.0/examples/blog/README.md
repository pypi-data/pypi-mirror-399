# Blog 示例项目

**完整的博客系统示例**

---

## 📖 项目简介

这是一个使用 FastAPI Scaffold 构建的完整博客系统示例，包含：

- ✅ 文章管理（CRUD）
- ✅ 评论系统
- ✅ 标签分类
- ✅ 用户认证
- ✅ 文章发布/草稿
- ✅ 搜索功能
- ✅ 分页列表

---

## 🏗️ 项目结构

```
blog/
├── app/
│   ├── models/
│   │   ├── article.py       # 文章模型
│   │   ├── comment.py       # 评论模型
│   │   └── tag.py           # 标签模型
│   ├── schemas/
│   │   ├── article.py       # 文章 Schema
│   │   ├── comment.py       # 评论 Schema
│   │   └── tag.py           # 标签 Schema
│   ├── crud/
│   │   ├── article.py       # 文章 CRUD
│   │   ├── comment.py       # 评论 CRUD
│   │   └── tag.py           # 标签 CRUD
│   └── api/v1/
│       ├── articles.py      # 文章 API
│       ├── comments.py      # 评论 API
│       └── tags.py          # 标签 API
└── README.md                # 本文件
```

---

## 🚀 快速开始

### 方式一: 使用 Droid 生成（推荐）

**在 Factory 界面中调用 scaffold-generator Droid**:

```
需求描述：
创建一个博客系统，包含文章、评论和标签。

文章模块：
- 标题（必需，最多200字符）
- 内容（必需，长文本）
- 摘要（可选，最多500字符）
- 作者（关联用户表）
- 发布状态（布尔值，默认false）
- 发布时间（可选，日期时间）
- 浏览次数（整数，默认0）

评论模块：
- 内容（必需，长文本）
- 文章（关联文章表）
- 作者（关联用户表）
- 父评论（可选，自关联，支持回复）

标签模块：
- 名称（必需，唯一，最多50字符）
- 描述（可选，最多200字符）
- 文章数量（整数，默认0）

项目名称：blog-system
数据库：sqlite
认证：是
```

**Droid 自动完成**:
1. ✅ 解析 3 个实体
2. ✅ 推断所有字段
3. ✅ 生成完整项目
4. ✅ 配置关系
5. ✅ 初始化数据库
6. ✅ 验证通过

**时间**: ~2 分钟

### 方式二: 使用 CLI 手动生成

```bash
# 1. 创建项目
cd fastapi-scaffold
python cli/main.py init blog-system

# 2. 进入项目
cd blog-system

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 生成文章模块
python ../cli/main.py generate crud article \
  --fields="title:str,content:text,summary:text?,author_id:int,published:bool,published_at:datetime?,views:int" \
  --api

# 6. 生成评论模块
python ../cli/main.py generate crud comment \
  --fields="content:text,article_id:int,author_id:int,parent_id:int?" \
  --api

# 7. 生成标签模块
python ../cli/main.py generate crud tag \
  --fields="name:str,description:text?,article_count:int" \
  --api

# 8. 注册路由（手动编辑 app/main.py）
# from app.api.v1 import articles, comments, tags
# app.include_router(articles.router)
# app.include_router(comments.router)
# app.include_router(tags.router)

# 9. 初始化数据库
python ../cli/main.py db init

# 10. 启动服务器
uvicorn app.main:app --reload
```

---

## 📝 数据模型

### Article（文章）

```python
class Article(Base):
    __tablename__ = "articles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    published: Mapped[bool] = mapped_column(default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    views: Mapped[int] = mapped_column(default=0)
    
    # 关系
    author: Mapped["User"] = relationship(back_populates="articles")
    comments: Mapped[List["Comment"]] = relationship(back_populates="article")
    tags: Mapped[List["Tag"]] = relationship(
        secondary="article_tags",
        back_populates="articles"
    )
```

### Comment（评论）

```python
class Comment(Base):
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id"),
        nullable=True
    )
    
    # 关系
    article: Mapped["Article"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship()
    parent: Mapped[Optional["Comment"]] = relationship(
        remote_side="Comment.id",
        back_populates="replies"
    )
    replies: Mapped[List["Comment"]] = relationship(
        back_populates="parent"
    )
```

### Tag（标签）

```python
class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    article_count: Mapped[int] = mapped_column(default=0)
    
    # 关系
    articles: Mapped[List["Article"]] = relationship(
        secondary="article_tags",
        back_populates="tags"
    )
```

---

## 🔗 API 端点

### 文章 API

```
GET    /api/v1/articles               # 获取文章列表（分页、搜索、筛选）
POST   /api/v1/articles               # 创建文章
GET    /api/v1/articles/{id}          # 获取文章详情
PUT    /api/v1/articles/{id}          # 更新文章
DELETE /api/v1/articles/{id}          # 删除文章
POST   /api/v1/articles/{id}/publish  # 发布文章
GET    /api/v1/articles/{id}/comments # 获取文章评论
GET    /api/v1/articles/published     # 获取已发布文章
```

### 评论 API

```
GET    /api/v1/comments           # 获取评论列表
POST   /api/v1/comments           # 创建评论
GET    /api/v1/comments/{id}      # 获取评论详情
PUT    /api/v1/comments/{id}      # 更新评论
DELETE /api/v1/comments/{id}      # 删除评论
GET    /api/v1/comments/{id}/replies  # 获取回复
```

### 标签 API

```
GET    /api/v1/tags               # 获取标签列表
POST   /api/v1/tags               # 创建标签
GET    /api/v1/tags/{id}          # 获取标签详情
PUT    /api/v1/tags/{id}          # 更新标签
DELETE /api/v1/tags/{id}          # 删除标签
GET    /api/v1/tags/{id}/articles # 获取标签的文章
```

---

## 📖 使用示例

### 1. 创建文章

```bash
# 登录获取 Token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 创建文章（草稿）
curl -X POST http://localhost:8000/api/v1/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的第一篇博客",
    "content": "这是文章内容...",
    "summary": "这是摘要",
    "published": false
  }'
```

### 2. 发布文章

```bash
# 发布文章
curl -X POST http://localhost:8000/api/v1/articles/1/publish \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 添加评论

```bash
# 添加评论
curl -X POST http://localhost:8000/api/v1/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "很好的文章！",
    "article_id": 1
  }'

# 回复评论
curl -X POST http://localhost:8000/api/v1/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "谢谢支持！",
    "article_id": 1,
    "parent_id": 1
  }'
```

### 4. 添加标签

```bash
# 创建标签
curl -X POST http://localhost:8000/api/v1/tags \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "description": "Python 相关文章"
  }'

# 给文章添加标签（需要在 API 中实现）
curl -X POST http://localhost:8000/api/v1/articles/1/tags \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag_id": 1}'
```

### 5. 搜索文章

```bash
# 搜索标题或内容
curl "http://localhost:8000/api/v1/articles?search=Python" \
  -H "Authorization: Bearer $TOKEN"

# 按标签筛选
curl "http://localhost:8000/api/v1/articles?tag_id=1" \
  -H "Authorization: Bearer $TOKEN"

# 只看已发布的
curl "http://localhost:8000/api/v1/articles/published" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 扩展功能

### 浏览统计

```python
# app/api/v1/articles.py
@router.get("/{id}")
def get_article(id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404)
    
    # 增加浏览次数
    article.views += 1
    db.commit()
    
    return article
```

### 热门文章

```python
@router.get("/popular")
def get_popular_articles(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取热门文章（按浏览量）"""
    return db.query(Article).filter(
        Article.published == True
    ).order_by(
        Article.views.desc()
    ).limit(limit).all()
```

### 文章标签关联

```python
# 多对多关系表
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

# API 端点
@router.post("/{id}/tags")
def add_tag_to_article(
    id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(Article.id == id).first()
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not article or not tag:
        raise HTTPException(status_code=404)
    
    article.tags.append(tag)
    tag.article_count += 1
    db.commit()
    
    return {"message": "Tag added"}
```

---

## 📊 数据示例

### 种子数据

```python
# scripts/init_db.py

# 创建标签
tags = [
    Tag(name="Python", description="Python 编程语言"),
    Tag(name="FastAPI", description="FastAPI 框架"),
    Tag(name="数据库", description="数据库相关"),
]
db.add_all(tags)
db.flush()

# 创建文章
articles = [
    Article(
        title="FastAPI 入门教程",
        content="这是一篇关于 FastAPI 的入门教程...",
        summary="学习 FastAPI 的基础知识",
        author_id=admin.id,
        published=True,
        published_at=datetime.utcnow(),
        views=100
    ),
    Article(
        title="Python 最佳实践",
        content="本文介绍 Python 开发的最佳实践...",
        summary="提高 Python 代码质量",
        author_id=admin.id,
        published=True,
        published_at=datetime.utcnow(),
        views=50
    ),
]
db.add_all(articles)
db.flush()

# 关联标签
articles[0].tags.extend([tags[0], tags[1]])
articles[1].tags.append(tags[0])

# 创建评论
comments = [
    Comment(
        content="很好的教程！",
        article_id=articles[0].id,
        author_id=admin.id
    ),
    Comment(
        content="谢谢分享！",
        article_id=articles[0].id,
        author_id=admin.id,
        parent_id=1  # 回复第一条评论
    ),
]
db.add_all(comments)
db.commit()
```

---

## 🎨 前端集成

### Vue 3 示例

```vue
<template>
  <div class="blog">
    <h1>博客列表</h1>
    <div v-for="article in articles" :key="article.id">
      <h2>{{ article.title }}</h2>
      <p>{{ article.summary }}</p>
      <span>👁️ {{ article.views }} | 💬 {{ article.comments_count }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const articles = ref([])

const fetchArticles = async () => {
  const response = await fetch('http://localhost:8000/api/v1/articles/published')
  articles.value = await response.json()
}

onMounted(() => {
  fetchArticles()
})
</script>
```

---

## 🚀 部署

参考主文档的部署章节（TUTORIAL.md #9）

---

## 📚 参考

- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **SQLAlchemy 文档**: https://docs.sqlalchemy.org/
- **Pydantic 文档**: https://docs.pydantic.dev/

---

**版本**: v1.0.0  
**创建**: 2026-01-01
