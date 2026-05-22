from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.crud import sanction as crud_sanction
from app.crud import report as crud_report
from app.schemas.sanction import SanctionCreate, SanctionOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/sanctions", response_model=SanctionOut, status_code=201)
def create_sanction(
    data: SanctionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """관리자가 사용자에게 제재 부과"""
    target = db.query(User).filter(User.id == data.user_id).first()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "대상 사용자를 찾을 수 없습니다")
    if target.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "자기 자신에게 제재를 부과할 수 없습니다")

    return crud_sanction.create_sanction(db, data, issued_by=admin.id)


@router.get("/sanctions/user/{user_id}", response_model=list[SanctionOut])
def list_user_sanctions(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """특정 사용자의 제재 이력 (활성/만료 모두)"""
    return crud_sanction.list_user_sanctions(db, user_id)


@router.delete("/sanctions/{sanction_id}", response_model=SanctionOut)
def revoke_sanction(
    sanction_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """제재 해제 (오부과 정정 등)"""
    s = crud_sanction.revoke_sanction(db, sanction_id)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "제재를 찾을 수 없습니다")
    return s


@router.get("/reports/against/{user_id}/count")
def count_reports_against(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """특정 사용자가 받은 신고 총수 (제재 결정 참고용)"""
    return {"user_id": user_id, "total_reports": crud_report.count_reports_against(db, user_id)}

@router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """관리자가 사용자 계정 강제 삭제 (악성 사용자 등)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "사용자를 찾을 수 없습니다")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "관리자 본인 계정은 삭제할 수 없습니다")

    db.delete(user)
    db.commit()