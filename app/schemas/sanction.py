from datetime import datetime
from pydantic import BaseModel, Field
from app.models.sanction import SanctionType


class SanctionCreate(BaseModel):
    user_id: int
    type: SanctionType
    reason: str = Field(min_length=1, max_length=1000)
    duration_days: int | None = Field(
        default=None, ge=1, le=365,
        description="SUSPENSION일 때만 사용. 1~365일. BAN/WARNING은 무시됨",
    )


class SanctionOut(BaseModel):
    id: int
    user_id: int
    type: SanctionType
    reason: str
    issued_by: int | None
    starts_at: datetime
    expires_at: datetime | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True