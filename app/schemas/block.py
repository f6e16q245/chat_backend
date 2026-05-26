from datetime import datetime
from pydantic import BaseModel


class BlockCreate(BaseModel):
    blocked_id: int


class BlockedUser(BaseModel):
    id: int
    nickname: str
    avatar: str

    class Config:
        from_attributes = True


class BlockOut(BaseModel):
    id: int
    blocker_id: int
    blocked_id: int
    blocked_user: BlockedUser
    created_at: datetime

    class Config:
        from_attributes = True