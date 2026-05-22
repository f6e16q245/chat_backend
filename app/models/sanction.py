from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class SanctionType(str, enum.Enum):
    WARNING = "warning"        # 경고
    SUSPENSION = "suspension"  # 일시 정지
    BAN = "ban"                # 영구 정지


class Sanction(Base):
    __tablename__ = "sanctions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(SanctionType), nullable=False)
    reason = Column(Text, nullable=False)              # 제재 사유
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 관리자 id (자동 부과는 NULL)
    starts_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)       # NULL이면 영구 (BAN/WARNING)
    is_active = Column(Boolean, default=True, nullable=False)  # 수동 해제 가능
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    issuer = relationship("User", foreign_keys=[issued_by])