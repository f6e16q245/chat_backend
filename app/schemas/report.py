from datetime import datetime
from pydantic import BaseModel, Field
from app.models.report import ReportReason, ReportStatus


class ReportCreate(BaseModel):
    reported_id: int
    reason: ReportReason
    detail: str = Field(default="", max_length=1000)


class ReportOut(BaseModel):
    id: int
    reporter_id: int
    reported_id: int
    reason: ReportReason
    detail: str
    status: ReportStatus
    created_at: datetime
    reviewed_at: datetime | None

    class Config:
        from_attributes = True