"""DB Command - Database Management"""
import click
import subprocess
import sys
from pathlib import Path


@click.group()
def db():
    """
    Database management commands
    
    Examples:
      scaffold db init        # Initialize database
      scaffold db reset       # Reset database
    """
    pass


@db.command()
def init():
    """Initialize database with schema and seed data"""
    # 检查是否在项目根目录
    if not Path('scripts/init_db.py').exists():
        click.echo(click.style(
            "Error: scripts/init_db.py not found",
            fg='red', bold=True
        ))
        click.echo("Please run this command from the project root")
        sys.exit(1)
    
    click.echo(click.style("Initializing database...", fg='cyan', bold=True))
    
    try:
        result = subprocess.run(
            ['python', 'scripts/init_db.py'],
            capture_output=False,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            click.echo()
            click.echo(click.style("[OK] Database initialized successfully!", fg='green', bold=True))
        else:
            click.echo(click.style("[FAIL] Database initialization failed", fg='red', bold=True))
            sys.exit(1)
    
    except subprocess.TimeoutExpired:
        click.echo(click.style("[FAIL] Database initialization timed out", fg='red', bold=True))
        sys.exit(1)
    
    except Exception as e:
        click.echo(click.style(f"[FAIL] Error: {e}", fg='red', bold=True))
        sys.exit(1)


@db.command()
@click.option('--backup', is_flag=True, help='Backup database before reset')
@click.confirmation_option(prompt='This will delete all data. Continue?')
def reset(backup):
    """Reset database (WARNING: deletes all data)"""
    db_file = Path('app.db')
    
    if not db_file.exists():
        click.echo("Database file not found, creating new...")
    else:
        # 备份（如果需要）
        if backup:
            import shutil
            from datetime import datetime
            backup_file = f"app.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(db_file, backup_file)
            click.echo(f"Database backed up to: {backup_file}")
        
        # 删除数据库
        db_file.unlink()
        click.echo("Database deleted")
    
    # 重新初始化
    click.echo()
    click.echo(click.style("Reinitializing database...", fg='cyan', bold=True))
    
    try:
        result = subprocess.run(
            ['python', 'scripts/init_db.py'],
            capture_output=False,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            click.echo()
            click.echo(click.style("[OK] Database reset successfully!", fg='green', bold=True))
        else:
            click.echo(click.style("[FAIL] Database reset failed", fg='red', bold=True))
            sys.exit(1)
    
    except Exception as e:
        click.echo(click.style(f"[FAIL] Error: {e}", fg='red', bold=True))
        sys.exit(1)


@db.command()
def migrate():
    """Generate database migration (placeholder)"""
    click.echo(click.style("Database migration support coming soon!", fg='yellow'))
    click.echo()
    click.echo("For now, you can:")
    click.echo("  1. Modify your models in app/models/")
    click.echo("  2. Run: scaffold db reset --backup")
    click.echo("  3. Or use Alembic directly for migrations")


@db.command()
def upgrade():
    """Apply database migrations (placeholder)"""
    click.echo(click.style("Database migration support coming soon!", fg='yellow'))


if __name__ == '__main__':
    db()
