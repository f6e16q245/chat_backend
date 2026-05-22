import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.verification import EmailVerificationCode
from app.core.config import settings


def _generate_code() -> str:
    """6자리 숫자 코드 생성 (앞에 0이 와도 유지)"""
    return f"{random.randint(0, 999999):06d}"


def issue_code(db: Session, user_id: int) -> str:
    """
    새 코드 발급.
    이미 발급된 미사용 코드가 있으면 모두 만료시키고 새로 발급.
    """
    # 기존 미만료 코드들을 모두 만료시킴 (즉시 expires_at을 과거로)
    db.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_id == user_id,
        EmailVerificationCode.expires_at > datetime.utcnow(),
    ).update({"expires_at": datetime.utcnow()})

    code = _generate_code()
    record = EmailVerificationCode(
        user_id=user_id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.EMAIL_CODE_EXPIRE_MINUTES),
    )
    db.add(record)
    db.commit()
    return code


def verify_code(db: Session, user_id: int, code: str) -> tuple[bool, str]:
    """
    코드 검증.
    반환: (성공여부, 메시지)
    """
    record = (
        db.query(EmailVerificationCode)
        .filter(EmailVerificationCode.user_id == user_id)
        .order_by(EmailVerificationCode.created_at.desc())
        .first()
    )

    if not record:
        return False, "발급된 인증 코드가 없습니다. 재발송을 요청해주세요."

    if record.expires_at < datetime.utcnow():
        return False, "인증 코드가 만료되었습니다. 재발송을 요청해주세요."

    if record.attempt_count >= settings.EMAIL_CODE_MAX_ATTEMPTS:
        return False, "시도 횟수를 초과했습니다. 재발송을 요청해주세요."

    # 시도 횟수 증가 (먼저 기록)
    record.attempt_count += 1
    db.commit()

    if record.code != code:
        remaining = settings.EMAIL_CODE_MAX_ATTEMPTS - record.attempt_count
        return False, f"코드가 일치하지 않습니다. (남은 시도: {remaining}회)"

    # 성공: 즉시 만료시켜 재사용 방지
    record.expires_at = datetime.utcnow()
    db.commit()
    return True, "인증 성공"