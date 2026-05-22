from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.sanction import Sanction, SanctionType
from app.schemas.sanction import SanctionCreate


def create_sanction(db: Session, data: SanctionCreate, issued_by: int | None) -> Sanction:
    expires_at = None
    if data.type == SanctionType.SUSPENSION:
        days = data.duration_days or 7  # 기본 7일
        expires_at = datetime.utcnow() + timedelta(days=days)
    # BAN, WARNING은 expires_at=None

    sanction = Sanction(
        user_id=data.user_id,
        type=data.type,
        reason=data.reason,
        issued_by=issued_by,
        expires_at=expires_at,
    )
    db.add(sanction)
    db.commit()
    db.refresh(sanction)
    return sanction


def get_active_blocking_sanction(db: Session, user_id: int) -> Sanction | None:
    """
    현재 로그인 차단 효력이 있는 제재가 있으면 반환.
    - BAN: 영구
    - SUSPENSION: expires_at 안 지났을 때
    - WARNING: 차단 효력 없음 (반환 대상 아님)
    """
    now = datetime.utcnow()
    return (
        db.query(Sanction)
        .filter(
            Sanction.user_id == user_id,
            Sanction.is_active == True,
            Sanction.type.in_([SanctionType.BAN, SanctionType.SUSPENSION]),
            or_(Sanction.expires_at.is_(None), Sanction.expires_at > now),
        )
        .order_by(Sanction.created_at.desc())
        .first()
    )


def list_user_sanctions(db: Session, user_id: int) -> list[Sanction]:
    return (
        db.query(Sanction)
        .filter(Sanction.user_id == user_id)
        .order_by(Sanction.created_at.desc())
        .all()
    )


def revoke_sanction(db: Session, sanction_id: int) -> Sanction | None:
    """제재 해제 (관리자가 잘못 부과한 거 되돌리기 등)"""
    sanction = db.query(Sanction).filter(Sanction.id == sanction_id).first()
    if not sanction:
        return None
    sanction.is_active = False
    db.commit()
    db.refresh(sanction)
    return sanction