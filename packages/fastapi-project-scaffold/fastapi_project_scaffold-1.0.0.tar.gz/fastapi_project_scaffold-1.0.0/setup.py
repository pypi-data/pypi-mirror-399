"""
FastAPI Scaffold - 企业级 FastAPI 项目脚手架工具
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取版本号
version = {}
with open("fastapi_scaffold/__version__.py", encoding='utf-8') as f:
    exec(f.read(), version)

setup(
    name="fastapi-project-scaffold",
    version=version['__version__'],
    author="Project Team",
    author_email="support@example.com",
    description="Enterprise-grade FastAPI project scaffold with CLI and AI-powered code generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/btrobot/fastapi-scaffold",
    project_urls={
        "Bug Tracker": "https://github.com/btrobot/fastapi-scaffold/issues",
        "Documentation": "https://github.com/btrobot/fastapi-scaffold/blob/main/README.md",
        "Source Code": "https://github.com/btrobot/fastapi-scaffold",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "fastapi",
        "scaffold",
        "cli",
        "code-generator",
        "template",
        "crud",
        "rest-api",
        "jwt",
        "rbac",
        "sqlalchemy",
        "pydantic",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fastapi-scaffold=fastapi_scaffold.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
)
