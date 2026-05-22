from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password
from app.models.user import User
from app.schemas.user import (
    UserOut, ProfileUpdate, PasswordChange, AccountDelete,
)
from app.crud import user as crud_user

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


@router.patch("/me/password")
def change_my_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, current.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "현재 비밀번호가 일치하지 않습니다")
    if data.current_password == data.new_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "새 비밀번호가 기존 비밀번호와 같습니다")

    crud_user.change_password(db, current, data.new_password)
    return {"message": "비밀번호가 변경되었습니다"}


@router.delete("/me", status_code=204)
def delete_my_account(
    data: AccountDelete,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """회원 탈퇴. 본인 비밀번호로 한 번 더 확인."""
    if not verify_password(data.password, current.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "비밀번호가 일치하지 않습니다")

    crud_user.delete_user(db, current)