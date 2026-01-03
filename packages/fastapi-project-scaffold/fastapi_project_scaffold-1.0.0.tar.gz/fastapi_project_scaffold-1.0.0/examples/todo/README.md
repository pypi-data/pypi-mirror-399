# Todo 示例项目

**简单实用的任务管理系统**

---

## 📖 项目简介

这是一个使用 FastAPI Scaffold 构建的 Todo 应用示例，包含：

- ✅ 任务列表管理
- ✅ 任务项 CRUD
- ✅ 任务状态管理
- ✅ 优先级设置
- ✅ 截止日期提醒
- ✅ 任务搜索和筛选

---

## 🏗️ 项目结构

```
todo/
├── app/
│   ├── models/
│   │   ├── task_list.py     # 任务列表模型
│   │   └── task_item.py     # 任务项模型
│   ├── schemas/
│   │   ├── task_list.py     # 任务列表 Schema
│   │   └── task_item.py     # 任务项 Schema
│   ├── crud/
│   │   ├── task_list.py     # 任务列表 CRUD
│   │   └── task_item.py     # 任务项 CRUD
│   └── api/v1/
│       ├── task_lists.py    # 任务列表 API
│       └── task_items.py    # 任务项 API
└── README.md                # 本文件
```

---

## 🚀 快速开始

### 方式一: 使用 Droid 生成

```
需求描述：
创建一个 Todo 任务管理系统，包含任务列表和任务项。

任务列表模块：
- 名称（必需，最多100字符）
- 描述（可选，最多500字符）
- 所有者（关联用户表）
- 任务数量（整数，默认0）
- 完成数量（整数，默认0）

任务项模块：
- 标题（必需，最多200字符）
- 描述（可选，长文本）
- 列表（关联任务列表）
- 所有者（关联用户表）
- 状态（枚举：todo/in_progress/done，默认todo）
- 优先级（枚举：low/medium/high，默认medium）
- 截止日期（可选，日期）
- 完成时间（可选，日期时间）

项目名称：todo-app
数据库：sqlite
认证：是
```

### 方式二: 使用 CLI 生成

```bash
# 1. 创建项目
python cli/main.py init todo-app
cd todo-app

# 2. 安装依赖
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 生成任务列表模块
python ../cli/main.py generate crud task_list \
  --fields="name:str,description:text?,owner_id:int,task_count:int,completed_count:int" \
  --api

# 4. 生成任务项模块
python ../cli/main.py generate crud task_item \
  --fields="title:str,description:text?,list_id:int,owner_id:int,status:str,priority:str,due_date:date?,completed_at:datetime?" \
  --api

# 5. 初始化数据库
python ../cli/main.py db init

# 6. 启动
uvicorn app.main:app --reload
```

---

## 📝 数据模型

### TaskList（任务列表）

```python
class TaskList(Base):
    __tablename__ = "task_lists"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_count: Mapped[int] = mapped_column(default=0)
    completed_count: Mapped[int] = mapped_column(default=0)
    
    # 关系
    owner: Mapped["User"] = relationship()
    tasks: Mapped[List["TaskItem"]] = relationship(back_populates="task_list")
    
    @property
    def progress(self) -> float:
        """完成进度（百分比）"""
        if self.task_count == 0:
            return 0.0
        return (self.completed_count / self.task_count) * 100
```

### TaskItem（任务项）

```python
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskItem(Base):
    __tablename__ = "task_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    list_id: Mapped[int] = mapped_column(ForeignKey("task_lists.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.MEDIUM)
    due_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # 关系
    task_list: Mapped["TaskList"] = relationship(back_populates="tasks")
    owner: Mapped["User"] = relationship()
    
    @property
    def is_overdue(self) -> bool:
        """是否已逾期"""
        if self.due_date and self.status != TaskStatus.DONE:
            return date.today() > self.due_date
        return False
```

---

## 🔗 API 端点

### 任务列表 API

```
GET    /api/v1/task-lists              # 获取任务列表
POST   /api/v1/task-lists              # 创建任务列表
GET    /api/v1/task-lists/{id}         # 获取详情
PUT    /api/v1/task-lists/{id}         # 更新
DELETE /api/v1/task-lists/{id}         # 删除
GET    /api/v1/task-lists/{id}/tasks   # 获取列表的任务
GET    /api/v1/task-lists/{id}/stats   # 获取统计信息
```

### 任务项 API

```
GET    /api/v1/tasks                   # 获取任务列表
POST   /api/v1/tasks                   # 创建任务
GET    /api/v1/tasks/{id}              # 获取详情
PUT    /api/v1/tasks/{id}              # 更新
DELETE /api/v1/tasks/{id}              # 删除
PATCH  /api/v1/tasks/{id}/status       # 更新状态
PATCH  /api/v1/tasks/{id}/priority     # 更新优先级
POST   /api/v1/tasks/{id}/complete     # 完成任务
GET    /api/v1/tasks/today             # 今日任务
GET    /api/v1/tasks/overdue           # 逾期任务
```

---

## 📖 使用示例

### 1. 创建任务列表

```bash
TOKEN="<your-token>"

# 创建任务列表
curl -X POST http://localhost:8000/api/v1/task-lists \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "工作任务",
    "description": "本周工作相关任务"
  }'
```

### 2. 添加任务

```bash
# 创建任务
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "完成项目文档",
    "description": "编写 API 文档和用户手册",
    "list_id": 1,
    "priority": "high",
    "due_date": "2026-01-05"
  }'
```

### 3. 更新任务状态

```bash
# 开始任务
curl -X PATCH http://localhost:8000/api/v1/tasks/1/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# 完成任务
curl -X POST http://localhost:8000/api/v1/tasks/1/complete \
  -H "Authorization: Bearer $TOKEN"
```

### 4. 查看今日任务

```bash
# 今日任务
curl http://localhost:8000/api/v1/tasks/today \
  -H "Authorization: Bearer $TOKEN"

# 逾期任务
curl http://localhost:8000/api/v1/tasks/overdue \
  -H "Authorization: Bearer $TOKEN"
```

### 5. 任务筛选

```bash
# 按状态筛选
curl "http://localhost:8000/api/v1/tasks?status=todo" \
  -H "Authorization: Bearer $TOKEN"

# 按优先级筛选
curl "http://localhost:8000/api/v1/tasks?priority=high" \
  -H "Authorization: Bearer $TOKEN"

# 按列表筛选
curl "http://localhost:8000/api/v1/tasks?list_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 扩展功能

### 今日任务

```python
@router.get("/today")
def get_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取今日任务"""
    today = date.today()
    return db.query(TaskItem).filter(
        TaskItem.owner_id == current_user.id,
        TaskItem.due_date == today,
        TaskItem.status != TaskStatus.DONE
    ).all()
```

### 逾期任务

```python
@router.get("/overdue")
def get_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取逾期任务"""
    today = date.today()
    return db.query(TaskItem).filter(
        TaskItem.owner_id == current_user.id,
        TaskItem.due_date < today,
        TaskItem.status != TaskStatus.DONE
    ).all()
```

### 完成任务

```python
@router.post("/{id}/complete")
def complete_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """完成任务"""
    task = db.query(TaskItem).filter(
        TaskItem.id == id,
        TaskItem.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404)
    
    # 更新任务状态
    task.status = TaskStatus.DONE
    task.completed_at = datetime.utcnow()
    
    # 更新列表统计
    task_list = task.task_list
    task_list.completed_count += 1
    
    db.commit()
    
    return task
```

### 任务统计

```python
@router.get("/{id}/stats")
def get_task_list_stats(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取任务列表统计"""
    task_list = db.query(TaskList).filter(
        TaskList.id == id,
        TaskList.owner_id == current_user.id
    ).first()
    
    if not task_list:
        raise HTTPException(status_code=404)
    
    # 统计各状态任务数
    tasks = db.query(TaskItem).filter(
        TaskItem.list_id == id
    ).all()
    
    return {
        "total": len(tasks),
        "todo": sum(1 for t in tasks if t.status == TaskStatus.TODO),
        "in_progress": sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
        "done": sum(1 for t in tasks if t.status == TaskStatus.DONE),
        "overdue": sum(1 for t in tasks if t.is_overdue),
        "progress": task_list.progress
    }
```

---

## 📊 数据示例

```python
# scripts/init_db.py

# 创建任务列表
task_lists = [
    TaskList(
        name="个人任务",
        description="个人日常任务",
        owner_id=admin.id,
        task_count=3,
        completed_count=1
    ),
    TaskList(
        name="工作任务",
        description="工作相关任务",
        owner_id=admin.id,
        task_count=2,
        completed_count=0
    ),
]
db.add_all(task_lists)
db.flush()

# 创建任务项
from datetime import timedelta

tasks = [
    TaskItem(
        title="买菜",
        description="买晚饭的食材",
        list_id=task_lists[0].id,
        owner_id=admin.id,
        status=TaskStatus.DONE,
        priority=TaskPriority.MEDIUM,
        due_date=date.today(),
        completed_at=datetime.utcnow()
    ),
    TaskItem(
        title="锻炼",
        description="跑步30分钟",
        list_id=task_lists[0].id,
        owner_id=admin.id,
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        due_date=date.today()
    ),
    TaskItem(
        title="学习 FastAPI",
        description="完成 FastAPI 教程",
        list_id=task_lists[0].id,
        owner_id=admin.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        due_date=date.today() + timedelta(days=3)
    ),
    TaskItem(
        title="项目评审",
        description="参加下午的项目评审会议",
        list_id=task_lists[1].id,
        owner_id=admin.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        due_date=date.today()
    ),
    TaskItem(
        title="周报",
        description="完成本周工作周报",
        list_id=task_lists[1].id,
        owner_id=admin.id,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        due_date=date.today() + timedelta(days=2)
    ),
]
db.add_all(tasks)
db.commit()
```

---

## 🎨 前端集成

### Vue 3 示例

```vue
<template>
  <div class="todo-app">
    <h1>我的任务</h1>
    
    <div class="stats">
      <span>总计: {{ stats.total }}</span>
      <span>待办: {{ stats.todo }}</span>
      <span>进行中: {{ stats.in_progress }}</span>
      <span>已完成: {{ stats.done }}</span>
    </div>
    
    <div class="task-list">
      <div v-for="task in tasks" :key="task.id" class="task-item">
        <input 
          type="checkbox" 
          :checked="task.status === 'done'"
          @change="toggleTask(task)"
        />
        <span :class="{'completed': task.status === 'done'}">
          {{ task.title }}
        </span>
        <span :class="'priority-' + task.priority">
          {{ task.priority }}
        </span>
        <span v-if="task.is_overdue" class="overdue">逾期</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const tasks = ref([])
const stats = ref({})

const fetchTasks = async () => {
  const response = await fetch('http://localhost:8000/api/v1/tasks', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
  tasks.value = await response.json()
}

const toggleTask = async (task) => {
  const newStatus = task.status === 'done' ? 'todo' : 'done'
  await fetch(`http://localhost:8000/api/v1/tasks/${task.id}/status`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status: newStatus })
  })
  fetchTasks()
}

onMounted(() => {
  fetchTasks()
})
</script>

<style>
.completed {
  text-decoration: line-through;
  color: #999;
}

.priority-high {
  color: red;
}

.overdue {
  color: orange;
  font-weight: bold;
}
</style>
```

---

## 🔔 提醒功能（可选）

```python
# 邮件提醒逾期任务
from fastapi import BackgroundTasks

def send_overdue_reminder(user_email: str, tasks: List[TaskItem]):
    """发送逾期提醒邮件"""
    # 发送邮件逻辑...
    pass

@router.get("/check-overdue")
def check_overdue_tasks(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查逾期任务并发送提醒"""
    overdue = db.query(TaskItem).filter(
        TaskItem.owner_id == current_user.id,
        TaskItem.due_date < date.today(),
        TaskItem.status != TaskStatus.DONE
    ).all()
    
    if overdue:
        background_tasks.add_task(
            send_overdue_reminder,
            current_user.email,
            overdue
        )
    
    return {"count": len(overdue)}
```

---

## 📚 参考

- **GTD (Getting Things Done)**: https://gettingthingsdone.com/
- **Todoist API**: https://developer.todoist.com/
- **Microsoft To Do**: https://to-do.microsoft.com/

---

**版本**: v1.0.0  
**创建**: 2026-01-01
