"""
数据库初始化脚本
使用 SQLAlchemy 创建表和初始数据
"""
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base, SessionLocal
from app.models import Role, Permission, User, role_permissions
from app.models.dict import DictType, DictData
from app.models.system_config import SystemConfig
from app.core.security import get_password_hash

print("=" * 60)
print("初始化数据库和基础数据")
print("=" * 60)

# 1. 创建所有表
print("\n步骤1: 创建数据库表...")
Base.metadata.create_all(bind=engine)
print("[OK] 数据库表创建成功")

# 2. 初始化基础数据
print("\n步骤2: 初始化基础数据...")
db = SessionLocal()

try:
    # 检查是否已初始化
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("[OK] 数据库已初始化，跳过")
        db.close()
        exit(0)
    
    # 创建角色
    admin_role = Role(
        name="admin",
        display_name="管理员",
        description="系统管理员，拥有所有权限"
    )
    user_role = Role(
        name="user",
        display_name="普通用户",
        description="普通用户，拥有基本权限"
    )
    db.add(admin_role)
    db.add(user_role)
    db.flush()  # 获取 role ID
    
    # 创建权限
    permissions = [
        Permission(resource="/api/users", action="POST", description="创建用户"),
        Permission(resource="/api/users", action="GET", description="查看用户"),
        Permission(resource="/api/users", action="PUT", description="更新用户"),
        Permission(resource="/api/users", action="DELETE", description="删除用户"),
        Permission(resource="/api/roles", action="POST", description="创建角色"),
        Permission(resource="/api/roles", action="GET", description="查看角色"),
        Permission(resource="/api/roles", action="PUT", description="更新角色"),
        Permission(resource="/api/roles", action="DELETE", description="删除角色"),
        Permission(resource="/api/permissions", action="POST", description="创建权限"),
        Permission(resource="/api/permissions", action="GET", description="查看权限"),
        Permission(resource="/api/permissions", action="PUT", description="更新权限"),
        Permission(resource="/api/permissions", action="DELETE", description="删除权限"),
        Permission(resource="/api/*", action="*", description="管理员所有权限"),
    ]
    
    for perm in permissions:
        db.add(perm)
    db.flush()
    
    # 给 admin 角色分配所有权限
    admin_perm = db.query(Permission).filter(
        Permission.resource == "/api/*",
        Permission.action == "*"
    ).first()
    if admin_perm:
        admin_role.permissions.append(admin_perm)
    
    # 给 user 角色分配基础权限（只读权限）
    user_perms = db.query(Permission).filter(
        Permission.action == "GET"
    ).all()
    for perm in user_perms:
        user_role.permissions.append(perm)
    
    # 创建管理员用户
    admin_user = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        role_id=admin_role.id,
        is_active=True,
        is_deleted=False
    )
    db.add(admin_user)
    
    # 创建示例字典类型
    dict_types = [
        DictType(type_code="system_status", type_name="系统状态", description="系统状态字典"),
        DictType(type_code="user_status", type_name="用户状态", description="用户状态字典"),
    ]
    for dt in dict_types:
        db.add(dt)
    db.flush()
    
    # 创建示例字典数据
    dict_data = [
        DictData(type_code="system_status", dict_code="active", dict_label="运行中", dict_value="active", sort_order=1, is_active=True),
        DictData(type_code="system_status", dict_code="maintenance", dict_label="维护中", dict_value="maintenance", sort_order=2, is_active=True),
        DictData(type_code="user_status", dict_code="active", dict_label="激活", dict_value="active", sort_order=1, is_active=True),
        DictData(type_code="user_status", dict_code="inactive", dict_label="禁用", dict_value="inactive", sort_order=2, is_active=True),
    ]
    for dd in dict_data:
        db.add(dd)
    
    # 创建示例系统配置
    configs = [
        SystemConfig(
            config_key="system.name",
            config_value="FastAPI-RBAC-Scaffold",
            config_group="system",
            config_type="string",
            label="系统名称",
            is_public=True,
            description="系统名称"
        ),
        SystemConfig(
            config_key="system.version",
            config_value="1.0.0",
            config_group="system",
            config_type="string",
            label="系统版本",
            is_public=True,
            description="系统版本"
        ),
    ]
    for config in configs:
        db.add(config)
    
    db.commit()
    print("[OK] 基础数据初始化成功")
    
    # 3. 验证数据
    print("\n步骤3: 验证数据...")
    role_count = db.query(Role).count()
    permission_count = db.query(Permission).count()
    user_count = db.query(User).count()
    dict_type_count = db.query(DictType).count()
    dict_data_count = db.query(DictData).count()
    config_count = db.query(SystemConfig).count()
    
    print(f"[OK] 角色数: {role_count}")
    print(f"[OK] 权限数: {permission_count}")
    print(f"[OK] 用户数: {user_count}")
    print(f"[OK] 字典类型数: {dict_type_count}")
    print(f"[OK] 字典数据数: {dict_data_count}")
    print(f"[OK] 系统配置数: {config_count}")
    
    admin = db.query(User).filter(User.username == "admin").first()
    if admin and admin.role:
        print(f"\n管理员信息:")
        print(f"  用户名: {admin.username}")
        print(f"  角色: {admin.role.name} ({admin.role.display_name})")
        print(f"  状态: {'激活' if admin.is_active else '禁用'}")
    
    print("\n" + "=" * 60)
    print("初始化完成！")
    print("=" * 60)
    print("\n登录信息:")
    print("  用户名: admin")
    print("  密码: admin123")
    print("\n请启动后端服务器:")
    print("  uvicorn app.main:app --reload")
    print("\n访问 API 文档:")
    print("  http://localhost:8000/docs")
    
except Exception as e:
    print(f"\n[ERROR] 错误: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    exit(1)
finally:
    db.close()
