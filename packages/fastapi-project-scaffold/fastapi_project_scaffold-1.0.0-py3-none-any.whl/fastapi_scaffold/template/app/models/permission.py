from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.role import Role


class Permission(Base):
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resource: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    roles: Mapped[List["Role"]] = relationship(secondary="role_permissions", back_populates="permissions", lazy="select")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
