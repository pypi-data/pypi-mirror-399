"""FastAPI Scaffold CLI - Main Entry Point"""
import click
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands.init import init
from cli.commands.check import check
from cli.commands.db import db
from cli.commands.generate import generate


@click.group()
@click.version_option(version='1.0.0', prog_name='scaffold')
@click.pass_context
def cli(ctx):
    """
    FastAPI Scaffold - 企业级 FastAPI 脚手架工具
    
    快速初始化项目，自动生成代码，提升开发效率。
    
    Examples:
      scaffold init my-project
      scaffold generate crud article --fields="title:str,content:text"
      scaffold check --all
    """
    ctx.ensure_object(dict)


# 注册命令
cli.add_command(init)
cli.add_command(check)
cli.add_command(db)
cli.add_command(generate)


if __name__ == '__main__':
    cli()
