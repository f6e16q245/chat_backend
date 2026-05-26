from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserOut, Token,
    EmailVerifyRequest, ResendCodeRequest,
)
from app.crud import user as crud_user
from app.crud import verification as crud_verify
from app.core.security import verify_password, create_access_token
from app.utils.mail import send_verification_code

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=201)
async def signup(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if crud_user.get_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "이미 가입된 이메일")
    
        # 인증 코드 발급 + 메일 발송 (메일은 백그라운드로)
    # code = crud_verify.issue_code(db, user.id)
    # background_tasks.add_task(send_verification_code, user.email, code)

    user = crud_user.create_user(db, data)
    # 발표 시연용: 이메일 인증 단계 자동 통과 (is_verified=True)
    # 클라우드 환경(Render Free)의 SMTP 차단으로 메일 발송 생략

    return user


@router.post("/verify-email")
def verify_email(data: EmailVerifyRequest, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, data.email)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "사용자를 찾을 수 없습니다")

    if user.is_verified:
        return {"message": "이미 인증된 계정입니다"}

    ok, msg = crud_verify.verify_code(db, user.id, data.code)
    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)

    user.is_verified = True
    db.commit()
    return {"message": "이메일 인증이 완료되었습니다. 이제 로그인하실 수 있습니다."}


@router.post("/resend-code")
async def resend_code(
    data: ResendCodeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = crud_user.get_by_email(db, data.email)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "사용자를 찾을 수 없습니다")
    if user.is_verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "이미 인증된 계정입니다")

    code = crud_verify.issue_code(db, user.id)
    background_tasks.add_task(send_verification_code, user.email, code)
    return {"message": "인증 코드를 다시 발송했습니다"}


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다")
    if not user.is_verified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "이메일 인증이 필요합니다. 받은 메일의 코드로 인증을 완료해주세요.",
        )

    # 제재 검사
    from app.crud import sanction as crud_sanction
    active = crud_sanction.get_active_blocking_sanction(db, user.id)
    if active:
        if active.type.value == "ban":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "영구 정지된 계정입니다.")
        else:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"계정이 정지되었습니다. (해제 예정: {active.expires_at.isoformat()}) 사유: {active.reason}",
            )

    return Token(access_token=create_access_token(user.id))

from app.schemas.user import PasswordResetRequest, PasswordResetConfirm
from app.utils.mail import send_password_reset_code
from app.crud import verification as crud_verify
from app.crud.user import change_password


@router.post("/password-reset/request")
async def password_reset_request(
    data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """비밀번호 재설정 코드 발송."""
    user = crud_user.get_by_email(db, data.email)
    # 보안상, 사용자 존재 여부를 알려주지 않음 (이메일 추측 공격 방지)
    if user:
        code = crud_verify.issue_code(db, user.id)
        background_tasks.add_task(send_password_reset_code, user.email, code)

    return {"message": "해당 이메일이 가입돼 있다면 재설정 코드를 발송했습니다"}


@router.post("/password-reset/confirm")
def password_reset_confirm(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """코드 검증 후 새 비밀번호 적용."""
    user = crud_user.get_by_email(db, data.email)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "유효하지 않은 요청입니다")

    ok, msg = crud_verify.verify_code(db, user.id, data.code)
    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)

    change_password(db, user, data.new_password)
    return {"message": "비밀번호가 재설정되었습니다. 새 비밀번호로 로그인해주세요."}