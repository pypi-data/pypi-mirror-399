from __future__ import annotations

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.refresh_token import RefreshToken


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id"))
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column()
    password_changed_at: Mapped[Optional[datetime]] = mapped_column()
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    role: Mapped[Optional["Role"]] = relationship(back_populates="users")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
