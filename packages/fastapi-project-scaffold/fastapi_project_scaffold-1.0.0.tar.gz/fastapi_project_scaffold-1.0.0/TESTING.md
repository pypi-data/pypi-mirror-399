# 打包测试指南

**FastAPI Scaffold 打包测试说明**

---

## 📋 测试环境准备

### 1. 安装构建工具

```bash
# 在项目虚拟环境中安装
pip install --upgrade setuptools wheel build twine
```

### 2. 验证环境

```bash
# 检查 Python 版本
python --version  # 应该 >= 3.10

# 检查工具
python -m build --version
twine --version
```

---

## 🔨 本地构建测试

### 1. 清理旧构建

```bash
# Windows PowerShell
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }
Get-ChildItem -Filter "*.egg-info" -Recurse | Remove-Item -Recurse -Force

# Linux/Mac
rm -rf dist build *.egg-info
```

### 2. 构建包

```bash
# 使用 build 模块（推荐）
python -m build

# 或使用 setup.py（传统方式）
python setup.py sdist bdist_wheel
```

### 3. 检查构建结果

```bash
# 应该生成两个文件
ls dist/
# fastapi_scaffold-1.0.0-py3-none-any.whl
# fastapi_scaffold-1.0.0.tar.gz

# 检查包
twine check dist/*
```

---

## 🧪 本地安装测试

### 1. 创建测试环境

```bash
# 创建新的虚拟环境
python -m venv test_env

# 激活
# Windows
test_env\Scripts\activate
# Linux/Mac
source test_env/bin/activate
```

### 2. 从本地安装

```bash
# 安装 wheel 包
pip install dist/fastapi_scaffold-1.0.0-py3-none-any.whl

# 或安装源码包
pip install dist/fastapi_scaffold-1.0.0.tar.gz
```

### 3. 测试 CLI 命令

```bash
# 测试命令是否可用
fastapi-scaffold --version

# 测试帮助
fastapi-scaffold --help

# 测试 init 命令
fastapi-scaffold init test-project
cd test-project
ls -la
```

### 4. 测试导入

```bash
# 测试 Python 导入
python -c "from fastapi_scaffold import __version__; print(__version__)"
python -c "from fastapi_scaffold.cli.main import cli; print('OK')"
```

### 5. 清理测试

```bash
# 退出虚拟环境
deactivate

# 删除测试文件
cd ..
rm -rf test_env test-project
```

---

## ✅ 验证清单

### 包结构验证

```bash
# 检查 wheel 内容
unzip -l dist/fastapi_scaffold-1.0.0-py3-none-any.whl

# 应包含:
- fastapi_scaffold/__init__.py
- fastapi_scaffold/__version__.py
- fastapi_scaffold/cli/
- fastapi_scaffold/template/
- *.dist-info/
```

### 元数据验证

```bash
# 检查包元数据
pip show fastapi-scaffold

# 应显示:
# Name: fastapi-scaffold
# Version: 1.0.0
# Summary: Enterprise-grade FastAPI project scaffold
# Author: Project Team
# License: MIT
```

### 功能验证

- [ ] CLI 命令可用 (`fastapi-scaffold --version`)
- [ ] init 命令可运行
- [ ] generate 命令可运行
- [ ] check 命令可运行
- [ ] db 命令可运行
- [ ] Python 导入正常
- [ ] 模板文件包含
- [ ] 文档文件包含

---

## 🐛 常见问题

### 问题 1: ModuleNotFoundError: No module named 'setuptools'

**解决**:
```bash
pip install --upgrade setuptools wheel
```

### 问题 2: ModuleNotFoundError: No module named 'build'

**解决**:
```bash
pip install --upgrade build
```

### 问题 3: 模板文件缺失

**检查**:
```bash
# 检查 MANIFEST.in
cat MANIFEST.in

# 检查 setup.py 的 package_data
grep -A 5 "package_data" setup.py
```

**解决**: 确保 MANIFEST.in 包含模板文件

### 问题 4: CLI 命令不可用

**检查**:
```bash
# 检查 entry_points
grep -A 5 "entry_points" setup.py

# 重新安装
pip uninstall fastapi-scaffold
pip install dist/*.whl
```

---

## 📊 测试报告模板

```markdown
# FastAPI Scaffold 打包测试报告

**测试日期**: 2026-01-01
**测试人员**: XXX
**版本**: 1.0.0

## 测试环境
- Python: 3.10.x
- OS: Windows 10 / Ubuntu 20.04 / macOS
- 虚拟环境: venv

## 测试结果

### 构建测试
- [ ] 清理旧构建: ✅/❌
- [ ] 源码包构建: ✅/❌
- [ ] wheel 包构建: ✅/❌
- [ ] twine check: ✅/❌

### 安装测试
- [ ] 安装成功: ✅/❌
- [ ] CLI 命令可用: ✅/❌
- [ ] Python 导入正常: ✅/❌

### 功能测试
- [ ] init 命令: ✅/❌
- [ ] generate 命令: ✅/❌
- [ ] check 命令: ✅/❌
- [ ] db 命令: ✅/❌

### 包内容检查
- [ ] 模板文件: ✅/❌
- [ ] 文档文件: ✅/❌
- [ ] 元数据正确: ✅/❌

## 问题记录

1. [问题描述]
   - 解决方案: [解决方法]

## 总结

[测试总结]
```

---

## 🚀 下一步

测试通过后：

1. **TestPyPI 测试**
   ```bash
   twine upload --repository testpypi dist/*
   pip install --index-url https://test.pypi.org/simple/ fastapi-scaffold
   ```

2. **PyPI 正式发布**
   ```bash
   twine upload dist/*
   ```

3. **GitHub Release**
   - 创建 Git 标签
   - 上传构建文件
   - 发布 Release Notes

---

**版本**: v1.0.0  
**更新**: 2026-01-01
