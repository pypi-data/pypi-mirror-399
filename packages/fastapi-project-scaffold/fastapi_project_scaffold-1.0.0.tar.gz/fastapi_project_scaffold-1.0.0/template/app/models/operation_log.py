from datetime import datetime
from typing import Optional
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    username: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50), index=True)
    resource: Mapped[str] = mapped_column(String(100), index=True)
    resource_id: Mapped[Optional[int]] = mapped_column()
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
