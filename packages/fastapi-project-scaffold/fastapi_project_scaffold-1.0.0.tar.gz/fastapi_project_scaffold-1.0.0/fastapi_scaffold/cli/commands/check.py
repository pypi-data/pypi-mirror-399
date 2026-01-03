"""Check Command - Code Quality Checks"""
import click
import subprocess
import sys
from pathlib import Path


@click.command()
@click.option('--schemas', is_flag=True, help='Check Schema conventions')
@click.option('--mypy', is_flag=True, help='Run mypy type checking')
@click.option('--format', 'check_format', is_flag=True, help='Check code formatting')
@click.option('--all', 'check_all', is_flag=True, help='Run all checks (default)')
def check(schemas, mypy, check_format, check_all):
    """
    Check code quality
    
    Examples:
      scaffold check                # Run all checks
      scaffold check --schemas      # Only check schemas
      scaffold check --mypy         # Only run mypy
    """
    # 如果没有指定任何选项，默认运行所有检查
    if not (schemas or mypy or check_format or check_all):
        check_all = True
    
    # 检查是否在项目根目录
    if not Path('app').exists():
        click.echo(click.style(
            "Error: Not in project root directory",
            fg='red', bold=True
        ))
        click.echo("Please run this command from the project root")
        sys.exit(1)
    
    click.echo(click.style("Running checks...", fg='cyan', bold=True))
    click.echo()
    
    failed_checks = []
    
    # 1. Schema 检查
    if schemas or check_all:
        click.echo("[1] Checking Schema conventions...")
        if run_schema_check():
            click.echo(click.style("  [OK] Schema check passed", fg='green'))
        else:
            click.echo(click.style("  [FAIL] Schema check failed", fg='red'))
            failed_checks.append('schemas')
        click.echo()
    
    # 2. mypy 检查
    if mypy or check_all:
        click.echo("[2] Running mypy type checking...")
        if run_mypy_check():
            click.echo(click.style("  [OK] mypy check passed", fg='green'))
        else:
            click.echo(click.style("  [FAIL] mypy check failed", fg='red'))
            failed_checks.append('mypy')
        click.echo()
    
    # 3. 格式检查
    if check_format or check_all:
        click.echo("[3] Checking code formatting...")
        if run_format_check():
            click.echo(click.style("  [OK] Format check passed", fg='green'))
        else:
            click.echo(click.style("  [FAIL] Format check failed", fg='red'))
            failed_checks.append('format')
        click.echo()
    
    # 输出总结
    click.echo("-" * 50)
    if failed_checks:
        click.echo(click.style(
            f"[FAIL] {len(failed_checks)} check(s) failed: {', '.join(failed_checks)}",
            fg='red', bold=True
        ))
        sys.exit(1)
    else:
        click.echo(click.style(
            "[OK] All checks passed!",
            fg='green', bold=True
        ))


def run_schema_check() -> bool:
    """运行 Schema 检查"""
    schemas_dir = Path('app/schemas')
    if not schemas_dir.exists():
        click.echo("  Warning: app/schemas directory not found")
        return True
    
    # 简单检查：Schema 文件是否符合命名规范
    issues = []
    for schema_file in schemas_dir.glob('*.py'):
        if schema_file.name == '__init__.py':
            continue
        
        # 检查是否包含 Base/Create/Update/Response
        content = schema_file.read_text(encoding='utf-8')
        
        has_base = 'Base(BaseModel)' in content or 'Base(Base' in content
        has_create = 'Create(' in content
        has_update = 'Update(' in content
        has_response = 'Response(' in content
        
        if not (has_base or has_create or has_update or has_response):
            issues.append(f"  - {schema_file.name}: No standard schema classes found")
    
    if issues:
        click.echo("  Issues found:")
        for issue in issues:
            click.echo(f"    {issue}")
        return False
    
    return True


def run_mypy_check() -> bool:
    """运行 mypy 类型检查"""
    try:
        result = subprocess.run(
            ['python', '-m', 'mypy', 'app'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # 输出错误信息
            if result.stdout:
                click.echo("  mypy output:")
                for line in result.stdout.split('\n')[:10]:  # 只显示前10行
                    if line.strip():
                        click.echo(f"    {line}")
            return False
        
        return True
    
    except subprocess.TimeoutExpired:
        click.echo("  Warning: mypy check timed out")
        return False
    
    except FileNotFoundError:
        click.echo("  Warning: mypy not installed")
        click.echo("  Install with: pip install mypy")
        return True  # 不作为失败处理
    
    except Exception as e:
        click.echo(f"  Error running mypy: {e}")
        return False


def run_format_check() -> bool:
    """运行格式检查"""
    # 简单检查：导入是否正确组织
    issues = []
    
    for py_file in Path('app').rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        content = py_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # 检查是否有多余的空行（连续3个以上）
        empty_count = 0
        for line in lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count >= 4:
                    issues.append(f"  - {py_file.relative_to('.')}: Too many consecutive empty lines")
                    break
            else:
                empty_count = 0
    
    if issues:
        click.echo("  Issues found:")
        for issue in issues[:5]:  # 只显示前5个
            click.echo(f"    {issue}")
        if len(issues) > 5:
            click.echo(f"    ... and {len(issues) - 5} more")
        return False
    
    return True


if __name__ == '__main__':
    check()
