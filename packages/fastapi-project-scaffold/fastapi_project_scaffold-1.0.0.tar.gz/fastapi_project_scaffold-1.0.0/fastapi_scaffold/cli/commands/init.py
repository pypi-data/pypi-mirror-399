"""Init Command - Initialize New Project"""
import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils.file_ops import (
    copy_directory,
    replace_in_file,
    ensure_directory,
    is_valid_project_name
)


@click.command()
@click.argument('project_name')
@click.option('--db', type=click.Choice(['sqlite', 'postgres']), default='sqlite',
              help='Database type (default: sqlite)')
@click.option('--no-examples', is_flag=True,
              help='Exclude example code')
@click.option('--force', is_flag=True,
              help='Overwrite existing directory')
def init(project_name, db, no_examples, force):
    """
    Initialize a new FastAPI project
    
    Examples:
      scaffold init my-blog
      scaffold init ecommerce --db=postgres --no-examples
    """
    # 1. 验证项目名称
    if not is_valid_project_name(project_name):
        click.echo(click.style(
            f"Error: Invalid project name '{project_name}'",
            fg='red', bold=True
        ))
        click.echo("Project name must:")
        click.echo("  - Start with a letter")
        click.echo("  - Contain only letters, numbers, underscores, and hyphens")
        click.echo("  - Be 3-50 characters long")
        sys.exit(1)
    
    # 2. 检查目录是否存在
    project_path = Path.cwd() / project_name
    if project_path.exists() and not force:
        click.echo(click.style(
            f"Error: Directory '{project_name}' already exists",
            fg='red', bold=True
        ))
        click.echo("Use --force to overwrite")
        sys.exit(1)
    
    # 3. 获取模板目录
    cli_dir = Path(__file__).parent.parent
    template_dir = cli_dir.parent / 'template'
    
    if not template_dir.exists():
        click.echo(click.style(
            "Error: Template directory not found",
            fg='red', bold=True
        ))
        click.echo(f"Expected: {template_dir}")
        sys.exit(1)
    
    click.echo(click.style("Creating project...", fg='cyan', bold=True))
    
    # 4. 复制模板
    click.echo(f"  [1/5] Copying template files...")
    ignore_patterns = ['__pycache__', '*.pyc', '.pytest_cache', 'app.db']
    if project_path.exists():
        import shutil
        shutil.rmtree(project_path)
    
    copy_directory(template_dir, project_path, ignore_patterns)
    
    # 5. 替换变量
    click.echo(f"  [2/5] Configuring project...")
    
    # 替换 .env.example 中的配置
    env_file = project_path / '.env.example'
    if env_file.exists():
        if db == 'postgres':
            replace_in_file(env_file, {
                'sqlite:///./app.db': 'postgresql://user:password@localhost/dbname'
            })
    
    # 6. 删除示例代码（如果需要）
    if no_examples:
        click.echo(f"  [3/5] Removing example code...")
        examples_files = [
            project_path / 'app' / 'api' / 'examples.py',
            project_path / 'app' / 'models' / 'example.py',
            project_path / 'app' / 'schemas' / 'example.py',
        ]
        for file in examples_files:
            if file.exists():
                file.unlink()
        
        # 更新 main.py（移除 examples 路由）
        main_file = project_path / 'app' / 'main.py'
        if main_file.exists():
            content = main_file.read_text(encoding='utf-8')
            content = content.replace(', examples', '')
            content = content.replace('app.include_router(examples.router)\n', '')
            main_file.write_text(content, encoding='utf-8')
    else:
        click.echo(f"  [3/5] Keeping example code...")
    
    # 7. 创建 .env 文件
    click.echo(f"  [4/5] Creating .env file...")
    env_example = project_path / '.env.example'
    env_target = project_path / '.env'
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_target)
    
    # 8. 打印完成信息
    click.echo(f"  [5/5] Done!")
    click.echo()
    click.echo(click.style("[OK] Project created successfully!", fg='green', bold=True))
    click.echo()
    click.echo(click.style("Next steps:", fg='cyan', bold=True))
    click.echo(f"  1. cd {project_name}")
    click.echo(f"  2. python -m venv venv")
    click.echo(f"  3. source venv/bin/activate  # Windows: venv\\Scripts\\activate")
    click.echo(f"  4. pip install -r requirements.txt")
    click.echo(f"  5. python scripts/init_db.py")
    click.echo(f"  6. uvicorn app.main:app --reload")
    click.echo()
    click.echo(click.style("Access:", fg='cyan', bold=True))
    click.echo(f"  - API docs: http://localhost:8000/docs")
    click.echo(f"  - Health: http://localhost:8000/health")
    click.echo()
    click.echo(click.style("Default admin:", fg='cyan', bold=True))
    click.echo(f"  - Username: admin")
    click.echo(f"  - Password: admin123")


if __name__ == '__main__':
    init()
