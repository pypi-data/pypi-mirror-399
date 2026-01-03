"""Generate Command - Code Generation"""
import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils.file_ops import is_valid_module_name
from cli.utils.validators import parse_fields
from cli.utils.code_gen import (
    generate_model,
    generate_schema,
    generate_crud,
    generate_api,
    to_class_name
)


@click.group()
def generate():
    """
    Code generation commands
    
    Examples:
      scaffold generate crud article --fields="title:str,content:text"
      scaffold g api article --auth
    """
    pass


@generate.command()
@click.argument('module_name')
@click.option('--fields', required=True, help='Field definitions (e.g., "name:str,age:int")')
@click.option('--api', is_flag=True, help='Also generate API')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
def crud(module_name, fields, api, overwrite):
    """
    Generate CRUD module (Model + Schema + CRUD)
    
    Examples:
      scaffold generate crud article --fields="title:str,content:text,author_id:int"
      scaffold g crud product --fields="name:str,price:float,stock:int" --api
    """
    # 1. 验证模块名
    if not is_valid_module_name(module_name):
        click.echo(click.style(
            f"Error: Invalid module name '{module_name}'",
            fg='red', bold=True
        ))
        click.echo("Module name must:")
        click.echo("  - Start with a letter")
        click.echo("  - Contain only letters, numbers, and underscores")
        click.echo("  - Be 2-30 characters long")
        sys.exit(1)
    
    # 2. 检查是否在项目根目录
    if not Path('app').exists():
        click.echo(click.style(
            "Error: Not in project root directory",
            fg='red', bold=True
        ))
        click.echo("Please run this command from the project root")
        sys.exit(1)
    
    # 3. 解析字段
    try:
        parsed_fields = parse_fields(fields)
    except ValueError as e:
        click.echo(click.style(f"Error: {e}", fg='red', bold=True))
        sys.exit(1)
    
    if not parsed_fields:
        click.echo(click.style("Error: No fields provided", fg='red', bold=True))
        sys.exit(1)
    
    class_name = to_class_name(module_name)
    
    click.echo(click.style(f"Generating CRUD module: {module_name}", fg='cyan', bold=True))
    click.echo(f"  Class name: {class_name}")
    click.echo(f"  Fields: {len(parsed_fields)}")
    click.echo()
    
    # 4. 生成 Model
    click.echo("[1/3] Generating Model...")
    model_file = Path(f'app/models/{module_name}.py')
    
    if model_file.exists() and not overwrite:
        click.echo(click.style(f"  [SKIP] {model_file} already exists", fg='yellow'))
    else:
        model_code = generate_model(module_name, class_name, parsed_fields)
        model_file.write_text(model_code, encoding='utf-8')
        click.echo(click.style(f"  [OK] Created {model_file}", fg='green'))
    
    # 5. 生成 Schema
    click.echo("[2/3] Generating Schema...")
    schema_file = Path(f'app/schemas/{module_name}.py')
    
    if schema_file.exists() and not overwrite:
        click.echo(click.style(f"  [SKIP] {schema_file} already exists", fg='yellow'))
    else:
        schema_code = generate_schema(module_name, class_name, parsed_fields)
        schema_file.write_text(schema_code, encoding='utf-8')
        click.echo(click.style(f"  [OK] Created {schema_file}", fg='green'))
    
    # 6. 生成 CRUD
    click.echo("[3/3] Generating CRUD...")
    crud_file = Path(f'app/crud/{module_name}.py')
    
    if crud_file.exists() and not overwrite:
        click.echo(click.style(f"  [SKIP] {crud_file} already exists", fg='yellow'))
    else:
        crud_code = generate_crud(module_name, class_name)
        crud_file.write_text(crud_code, encoding='utf-8')
        click.echo(click.style(f"  [OK] Created {crud_file}", fg='green'))
    
    click.echo()
    click.echo(click.style("[OK] CRUD module generated successfully!", fg='green', bold=True))
    
    # 7. 生成 API（如果需要）
    if api:
        click.echo()
        generate_api_files(module_name, class_name, overwrite)
    
    # 8. 打印集成指引
    print_integration_guide(module_name, class_name, api)


@generate.command()
@click.argument('module_name')
@click.option('--auth/--no-auth', default=True, help='Add authentication')
@click.option('--prefix', default=None, help='API path prefix (default: /api/v1/<module>s)')
@click.option('--tags', default=None, help='OpenAPI tags')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
def api(module_name, auth, prefix, tags, overwrite):
    """
    Generate API routes
    
    Examples:
      scaffold generate api article --auth
      scaffold g api user --prefix=/api/v2/users --no-auth
    """
    # 1. 验证模块名
    if not is_valid_module_name(module_name):
        click.echo(click.style(
            f"Error: Invalid module name '{module_name}'",
            fg='red', bold=True
        ))
        sys.exit(1)
    
    # 2. 检查是否在项目根目录
    if not Path('app').exists():
        click.echo(click.style(
            "Error: Not in project root directory",
            fg='red', bold=True
        ))
        sys.exit(1)
    
    # 3. 检查 CRUD 是否存在
    crud_file = Path(f'app/crud/{module_name}.py')
    if not crud_file.exists():
        click.echo(click.style(
            f"Warning: CRUD file not found: {crud_file}",
            fg='yellow'
        ))
        click.echo("Generate CRUD first with: scaffold generate crud " + module_name)
        if not click.confirm("Continue anyway?"):
            sys.exit(1)
    
    class_name = to_class_name(module_name)
    
    click.echo(click.style(f"Generating API routes: {module_name}", fg='cyan', bold=True))
    
    generate_api_files(module_name, class_name, overwrite, auth, prefix, tags)
    
    # 打印集成指引
    print_api_integration_guide(module_name)


def generate_api_files(
    module_name: str,
    class_name: str,
    overwrite: bool = False,
    auth: bool = True,
    prefix: str = None,
    tags: str = None
):
    """生成 API 文件"""
    click.echo("Generating API routes...")
    
    # 确保 v1 目录存在
    v1_dir = Path('app/api/v1')
    v1_dir.mkdir(parents=True, exist_ok=True)
    
    # 确保 __init__.py 存在
    init_file = v1_dir / '__init__.py'
    if not init_file.exists():
        init_file.write_text('')
    
    api_file = v1_dir / f'{module_name}s.py'
    
    if api_file.exists() and not overwrite:
        click.echo(click.style(f"  [SKIP] {api_file} already exists", fg='yellow'))
    else:
        api_code = generate_api(module_name, class_name, prefix, tags, auth)
        api_file.write_text(api_code, encoding='utf-8')
        click.echo(click.style(f"  [OK] Created {api_file}", fg='green'))
    
    click.echo()
    click.echo(click.style("[OK] API routes generated successfully!", fg='green', bold=True))


def print_integration_guide(module_name: str, class_name: str, has_api: bool):
    """打印集成指引"""
    click.echo()
    click.echo(click.style("Next steps:", fg='cyan', bold=True))
    
    if has_api:
        click.echo(f"  1. Register route in app/main.py:")
        click.echo(f"     from app.api.v1 import {module_name}s")
        click.echo(f"     app.include_router({module_name}s.router)")
        click.echo()
        click.echo(f"  2. Update database:")
        click.echo(f"     python ../cli/main.py db reset --backup")
        click.echo()
        click.echo(f"  3. Test API:")
        click.echo(f"     curl http://localhost:8000/api/v1/{module_name}s")
    else:
        click.echo(f"  1. Update app/models/__init__.py:")
        click.echo(f"     from app.models.{module_name} import {class_name}")
        click.echo()
        click.echo(f"  2. Update database:")
        click.echo(f"     python ../cli/main.py db reset --backup")
        click.echo()
        click.echo(f"  3. Generate API (optional):")
        click.echo(f"     python ../cli/main.py generate api {module_name}")


def print_api_integration_guide(module_name: str):
    """打印 API 集成指引"""
    click.echo()
    click.echo(click.style("Next steps:", fg='cyan', bold=True))
    click.echo(f"  1. Register route in app/main.py:")
    click.echo(f"     from app.api.v1 import {module_name}s")
    click.echo(f"     app.include_router({module_name}s.router)")
    click.echo()
    click.echo(f"  2. Restart server and test:")
    click.echo(f"     curl http://localhost:8000/api/v1/{module_name}s")


if __name__ == '__main__':
    generate()
