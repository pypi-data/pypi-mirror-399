"""
FastAPI Scaffold
================

Enterprise-grade FastAPI project scaffold with CLI and AI-powered code generation.

Features:
- Project initialization with CLI
- CRUD code generation
- API route generation
- JWT authentication + RBAC
- SQLAlchemy 2.0 + Pydantic 2.0
- Intelligent Droid system

Basic usage:
    >>> from fastapi_scaffold.cli.main import cli
    >>> # Or use command line:
    >>> # fastapi-scaffold init my-project
"""

from fastapi_scaffold.__version__ import __version__

__all__ = ['__version__']
