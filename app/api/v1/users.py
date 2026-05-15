from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut, ProfileUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current: User = Depends(get_current_user)):
    return current


@router.patch("/me", response_model=UserOut)
def update_me(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.nickname is not None:
        exists = db.query(User).filter(
            User.nickname == data.nickname, User.id != current.id
        ).first()
        if exists:
            raise HTTPException(409, "이미 사용 중인 닉네임")
        current.nickname = data.nickname
    if data.bio is not None:
        current.bio = data.bio
    db.commit()
    db.refresh(current)
    return current