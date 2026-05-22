from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class ReportReason(str, enum.Enum):
    SPAM = "spam"                    # 스팸/광고
    HARASSMENT = "harassment"        # 욕설/괴롭힘
    INAPPROPRIATE = "inappropriate"  # 부적절한 내용
    IMPERSONATION = "impersonation"  # 사칭
    OTHER = "other"                  # 기타


class ReportStatus(str, enum.Enum):
    PENDING = "pending"      # 검토 대기
    REVIEWED = "reviewed"    # 검토 완료, 조치 없음
    ACTIONED = "actioned"    # 제재 조치 완료
    DISMISSED = "dismissed"  # 기각


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reported_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(SQLEnum(ReportReason), nullable=False)
    detail = Column(Text, default="")
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    reporter = relationship("User", foreign_keys=[reporter_id])
    reported = relationship("User", foreign_keys=[reported_id])