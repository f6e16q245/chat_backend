from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.utils.nickname import generate_nickname


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def _unique_nickname(db: Session, max_try: int = 10) -> str:
    for _ in range(max_try):
        nick = generate_nickname()
        if not db.query(User).filter(User.nickname == nick).first():
            return nick
    raise RuntimeError("닉네임 생성 실패")


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        nickname=_unique_nickname(db),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def change_password(db: Session, user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()