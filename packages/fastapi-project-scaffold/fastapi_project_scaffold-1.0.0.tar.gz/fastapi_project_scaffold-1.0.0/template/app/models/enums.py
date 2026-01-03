"""
枚举定义模块
定义系统中使用的所有固定枚举类型
"""
from enum import Enum


class Gender(str, Enum):
    """性别"""
    MALE = "male"
    FEMALE = "female"


class PersonnelStatus(str, Enum):
    """人员状态"""
    ACTIVE = "active"       # 在职
    RESIGNED = "resigned"   # 离职


class PersonStatus(str, Enum):
    """人员管理状态"""
    ACTIVE = "active"       # 在职
    RESIGNED = "resigned"   # 离职
    SUSPENDED = "suspended" # 停用


class TrainingSubjectStatus(str, Enum):
    """训练科目状态"""
    DRAFT = "draft"         # 草稿
    ACTIVE = "active"       # 启用
    ARCHIVED = "archived"   # 归档


class TrainingTaskStatus(str, Enum):
    """训练任务状态"""
    DRAFT = "draft"
    STARTED = "started"
    TRAINING = "training"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionType(str, Enum):
    """题目类型"""
    CHOICE = "choice"       # 选择题
    JUDGMENT = "judgment"   # 判断题
    ANSWER = "answer"       # 问答题
