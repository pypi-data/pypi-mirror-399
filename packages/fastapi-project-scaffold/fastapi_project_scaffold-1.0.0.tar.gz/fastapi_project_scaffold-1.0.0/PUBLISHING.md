# 发布指南

**FastAPI Scaffold 发布到 PyPI 的完整指南**

---

## 📋 发布前检查清单

### 1. 代码质量

```bash
# 类型检查
mypy fastapi_scaffold/

# 代码格式
black --check fastapi_scaffold/

# 代码规范
flake8 fastapi_scaffold/

# 测试
pytest tests/ --cov=fastapi_scaffold
```

### 2. 版本号

编辑 `fastapi_scaffold/__version__.py`:

```python
__version__ = "1.0.0"  # 遵循语义化版本
```

### 3. 文档

- [ ] README.md 完整
- [ ] CHANGELOG.md 更新
- [ ] 所有文档链接有效
- [ ] 示例代码可运行

### 4. 许可证

- [ ] LICENSE 文件存在
- [ ] 代码头部包含版权声明

---

## 🔨 构建包

### 1. 安装构建工具

```bash
pip install --upgrade build twine
```

### 2. 清理旧构建

```bash
# Windows
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path fastapi_scaffold.egg-info) { Remove-Item fastapi_scaffold.egg-info -Recurse -Force }

# Linux/Mac
rm -rf dist build *.egg-info
```

### 3. 构建包

```bash
# 构建源码包和 wheel
python -m build

# 输出
dist/
├── fastapi_scaffold-1.0.0-py3-none-any.whl
└── fastapi_scaffold-1.0.0.tar.gz
```

### 4. 检查包

```bash
# 检查包元数据
twine check dist/*

# 列出包内容
tar -tzf dist/fastapi_scaffold-1.0.0.tar.gz
unzip -l dist/fastapi_scaffold-1.0.0-py3-none-any.whl
```

---

## 🧪 本地测试

### 1. 创建测试环境

```bash
# 创建虚拟环境
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# 从本地安装
pip install dist/fastapi_scaffold-1.0.0-py3-none-any.whl
```

### 2. 测试命令

```bash
# 测试 CLI 命令
fastapi-scaffold --version
fastapi-scaffold --help

# 测试项目创建
fastapi-scaffold init test-project
cd test-project
ls -la

# 测试生成功能
fastapi-scaffold generate crud test --fields="name:str,age:int"
```

### 3. 测试导入

```bash
python -c "from fastapi_scaffold import __version__; print(__version__)"
python -c "from fastapi_scaffold.cli.main import cli; print('OK')"
```

### 4. 清理

```bash
# 退出虚拟环境
deactivate

# 删除测试
rm -rf test_env test-project
```

---

## 📤 发布到 TestPyPI

### 1. 注册 TestPyPI 账号

访问 https://test.pypi.org/account/register/

### 2. 创建 API Token

1. 登录 https://test.pypi.org/
2. Account settings → API tokens → Add API token
3. Token name: `fastapi-project-scaffold-upload`
4. Scope: `Entire account` (或指定项目)
5. 复制 Token（只显示一次）

### 3. 配置凭证

创建 `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHl...  # 你的 Token

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHl...  # 你的 Token
```

### 4. 上传到 TestPyPI

```bash
twine upload --repository testpypi dist/*
```

### 5. 测试安装

```bash
# 从 TestPyPI 安装
pip install --index-url https://test.pypi.org/simple/ fastapi-project-scaffold

# 测试
fastapi-scaffold --version
```

---

## 🚀 发布到 PyPI

### 1. 注册 PyPI 账号

访问 https://pypi.org/account/register/

### 2. 创建 API Token

同 TestPyPI 步骤

### 3. 最终检查

```bash
# 确认版本号
cat fastapi_scaffold/__version__.py

# 确认 CHANGELOG
cat CHANGELOG.md

# 确认包内容
twine check dist/*

# 确认 Git 状态
git status
git tag -a v1.0.0 -m "Release version 1.0.0"
```

### 4. 上传到 PyPI

```bash
twine upload dist/*
```

### 5. 验证发布

访问: https://pypi.org/project/fastapi-project-scaffold/

```bash
# 安装验证
pip install fastapi-project-scaffold

# 测试
fastapi-scaffold --version
fastapi-scaffold init test-app
```

---

## 🏷️ 创建 GitHub Release

### 1. 推送标签

```bash
git push origin main
git push origin v1.0.0
```

### 2. 创建 Release

1. 访问 GitHub 仓库
2. Releases → Draft a new release
3. Choose a tag: `v1.0.0`
4. Release title: `v1.0.0 - First Stable Release`
5. 描述:

```markdown
## 🎉 FastAPI Scaffold v1.0.0

First stable release of FastAPI Scaffold!

### ✨ Features

- CLI tools for project and module generation
- Intelligent Droid system with natural language interface
- Complete authentication and authorization (JWT + RBAC)
- 11 field types with intelligent inference
- 44-item CheckList validation
- Comprehensive documentation

### 📦 Installation

pip install fastapi-scaffold

### 📚 Documentation

- [Quick Start](QUICK_START.md)
- [Tutorial](TUTORIAL.md)
- [Best Practices](BEST_PRACTICES.md)
- [FAQ](FAQ.md)

### 🔗 Links

- PyPI: https://pypi.org/project/fastapi-project-scaffold/
- Documentation: https://github.com/btrobot/fastapi-scaffold
```

6. Attach binaries: 上传 `dist/` 中的文件
7. Publish release

---

## 🐳 Docker 镜像

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装 fastapi-scaffold
RUN pip install --no-cache-dir fastapi-scaffold

# 设置入口点
ENTRYPOINT ["fastapi-scaffold"]
CMD ["--help"]
```

### 2. 构建镜像

```bash
docker build -t fastapi-scaffold:1.0.0 .
docker tag fastapi-scaffold:1.0.0 fastapi-scaffold:latest
```

### 3. 测试镜像

```bash
docker run fastapi-scaffold:1.0.0 --version
docker run -v $(pwd):/work -w /work fastapi-scaffold:1.0.0 init my-project
```

### 4. 推送到 Docker Hub

```bash
# 登录
docker login

# 标记
docker tag fastapi-scaffold:1.0.0 yourusername/fastapi-scaffold:1.0.0
docker tag fastapi-scaffold:1.0.0 yourusername/fastapi-scaffold:latest

# 推送
docker push yourusername/fastapi-scaffold:1.0.0
docker push yourusername/fastapi-scaffold:latest
```

---

## 📊 发布后任务

### 1. 更新文档

- [ ] 更新 README 的安装说明
- [ ] 添加 PyPI 徽章
- [ ] 更新版本号引用

### 2. 社区推广

- [ ] 发布到 Reddit (r/Python, r/FastAPI)
- [ ] 发布到 HackerNews
- [ ] Twitter/X 公告
- [ ] Dev.to 文章
- [ ] 中文社区（掘金、知乎）

### 3. 监控

- [ ] PyPI 下载量
- [ ] GitHub Stars
- [ ] Issues 处理
- [ ] 用户反馈

---

## 🔄 后续版本发布

### 1. 准备新版本

```bash
# 创建分支
git checkout -b release/v1.1.0

# 更新版本号
# 编辑 fastapi_scaffold/__version__.py

# 更新 CHANGELOG
# 编辑 CHANGELOG.md
```

### 2. 测试和构建

```bash
# 运行测试
pytest tests/

# 构建包
rm -rf dist build *.egg-info
python -m build

# 测试 TestPyPI
twine upload --repository testpypi dist/*
```

### 3. 发布

```bash
# 合并到主分支
git checkout main
git merge release/v1.1.0

# 标记版本
git tag -a v1.1.0 -m "Release version 1.1.0"

# 推送
git push origin main
git push origin v1.1.0

# 发布到 PyPI
twine upload dist/*

# 创建 GitHub Release
```

---

## 🛠️ 故障排查

### 问题 1: 上传失败 "File already exists"

**解决**:
```bash
# 更新版本号
# 编辑 fastapi_scaffold/__version__.py

# 重新构建
rm -rf dist build *.egg-info
python -m build
```

### 问题 2: 导入错误

**解决**:
```bash
# 检查 MANIFEST.in
# 确保所有必需文件包含

# 检查 setup.py 的 package_data
# 确保模板文件包含
```

### 问题 3: CLI 命令不可用

**解决**:
```bash
# 检查 entry_points 配置
# setup.py 和 pyproject.toml

# 重新安装
pip uninstall fastapi-scaffold
pip install fastapi-scaffold
```

---

## 📚 参考资源

- [PyPI 打包指南](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 文档](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**版本**: v1.0.0  
**更新**: 2026-01-01
