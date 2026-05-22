from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.crud import report as crud_report
from app.crud import user as crud_user
from app.schemas.report import ReportCreate, ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportOut, status_code=201)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.reported_id == current.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "자기 자신은 신고할 수 없습니다")

    # 신고 대상 존재 확인
    target = db.query(User).filter(User.id == data.reported_id).first()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "신고 대상 사용자를 찾을 수 없습니다")

    return crud_report.create_report(db, current.id, data)


@router.get("/me", response_model=list[ReportOut])
def list_my_reports(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """내가 한 신고 목록"""
    return crud_report.list_my_reports(db, current.id)