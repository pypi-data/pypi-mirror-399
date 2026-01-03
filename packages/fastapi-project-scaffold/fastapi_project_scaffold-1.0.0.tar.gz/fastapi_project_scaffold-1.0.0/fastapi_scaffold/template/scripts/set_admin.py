"""设置用户角色"""
import sys
from app.database import SessionLocal
from app.models import User, Role


def main():
    if len(sys.argv) < 2:
        print("用法: python set_admin.py <username> [role_name]")
        print("示例: python set_admin.py admin super_admin")
        print("可用角色: super_admin, admin, user")
        sys.exit(1)
    
    username = sys.argv[1]
    role_name = sys.argv[2] if len(sys.argv) > 2 else "admin"
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"错误: 用户 '{username}' 不存在")
            sys.exit(1)
        
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            print(f"错误: 角色 '{role_name}' 不存在")
            sys.exit(1)
        
        user.role_id = role.id
        user.is_active = True
        user.is_deleted = False
        db.commit()
        
        print(f"[OK] 用户 '{username}' 角色已更新为 '{role.display_name}' ({role.name})")
        print(f"[OK] 用户状态: 激活")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
