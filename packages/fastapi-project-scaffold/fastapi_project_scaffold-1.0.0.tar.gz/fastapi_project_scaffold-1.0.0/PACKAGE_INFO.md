# 包信息说明

## 📦 包命名

### PyPI 包名
```
fastapi-project-scaffold
```

**安装命令**:
```bash
pip install fastapi-project-scaffold
```

### CLI 命令名
```
fastapi-scaffold
```

**使用示例**:
```bash
fastapi-scaffold --version
fastapi-scaffold init my-project
fastapi-scaffold generate crud article --fields="title:str,content:text"
```

### GitHub 仓库
```
https://github.com/btrobot/fastapi-scaffold
```

### Python 包名（内部）
```
fastapi_scaffold
```

**导入示例**:
```python
from fastapi_scaffold import __version__
from fastapi_scaffold.cli.main import cli
```

---

## 🔗 相关链接

### PyPI
- **主页**: https://pypi.org/project/fastapi-project-scaffold/
- **TestPyPI**: https://test.pypi.org/project/fastapi-project-scaffold/

### GitHub
- **仓库**: https://github.com/btrobot/fastapi-scaffold
- **Issues**: https://github.com/btrobot/fastapi-scaffold/issues
- **Discussions**: https://github.com/btrobot/fastapi-scaffold/discussions

### 文档
- **README**: https://github.com/btrobot/fastapi-scaffold/blob/main/README.md
- **Quick Start**: https://github.com/btrobot/fastapi-scaffold/blob/main/QUICK_START.md
- **Tutorial**: https://github.com/btrobot/fastapi-scaffold/blob/main/TUTORIAL.md
- **Best Practices**: https://github.com/btrobot/fastapi-scaffold/blob/main/BEST_PRACTICES.md
- **FAQ**: https://github.com/btrobot/fastapi-scaffold/blob/main/FAQ.md

---

## ⚠️ 重要说明

### 为什么包名和命令名不同？

1. **PyPI 包名** (`fastapi-project-scaffold`): 
   - 更具描述性
   - 避免命名冲突
   - 符合 PyPI 命名规范

2. **CLI 命令名** (`fastapi-scaffold`):
   - 简短易记
   - 便于日常使用
   - 符合CLI工具命名习惯

这是常见的做法，例如：
- `pip install black` → 命令 `black`
- `pip install python-dotenv` → 导入 `import dotenv`
- `pip install fastapi-project-scaffold` → 命令 `fastapi-scaffold`

### 版本信息

- **当前版本**: 1.0.0
- **发布日期**: 2026-01-01
- **许可证**: MIT

---

## 📝 更新日志

### v1.0.0 (2026-01-01)
- 初始发布
- 完整的 CLI 工具集
- 智能 Droid 系统
- 完整文档和示例

---

**最后更新**: 2026-01-01
