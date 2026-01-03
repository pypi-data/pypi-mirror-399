"""File Operations Utilities"""
import shutil
from pathlib import Path
from typing import Optional


def copy_directory(src: Path, dest: Path, ignore_patterns: Optional[list] = None):
    """
    复制目录
    
    Args:
        src: 源目录
        dest: 目标目录
        ignore_patterns: 忽略的文件模式列表
    """
    if ignore_patterns:
        ignore = shutil.ignore_patterns(*ignore_patterns)
    else:
        ignore = None
    
    shutil.copytree(src, dest, ignore=ignore, dirs_exist_ok=True)


def replace_in_file(file_path: Path, replacements: dict):
    """
    替换文件中的字符串
    
    Args:
        file_path: 文件路径
        replacements: 替换字典 {old: new}
    """
    content = file_path.read_text(encoding='utf-8')
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    file_path.write_text(content, encoding='utf-8')


def ensure_directory(path: Path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def is_valid_project_name(name: str) -> bool:
    """
    验证项目名称是否合法
    
    规则:
    - 只能包含字母、数字、下划线、连字符
    - 必须以字母开头
    - 长度 3-50 个字符
    """
    import re
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{2,49}$'
    return bool(re.match(pattern, name))


def is_valid_module_name(name: str) -> bool:
    """
    验证模块名称是否合法
    
    规则:
    - 只能包含字母、数字、下划线
    - 必须以字母开头
    - 长度 2-30 个字符
    """
    import re
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{1,29}$'
    return bool(re.match(pattern, name))
