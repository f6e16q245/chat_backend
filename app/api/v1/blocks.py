from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.crud import block as crud_block
from app.schemas.block import BlockCreate, BlockOut

router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.post("", response_model=BlockOut, status_code=201)
def block_user(
    data: BlockCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if data.blocked_id == current.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "자기 자신은 차단할 수 없습니다")

    target = db.query(User).filter(User.id == data.blocked_id).first()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "차단 대상 사용자를 찾을 수 없습니다")

    block = crud_block.create_block(db, current.id, data.blocked_id)
    if not block:
        raise HTTPException(status.HTTP_409_CONFLICT, "이미 차단한 사용자입니다")
    return block


@router.delete("/{blocked_id}", status_code=204)
def unblock_user(
    blocked_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ok = crud_block.delete_block(db, current.id, blocked_id)
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "차단 기록이 없습니다")


@router.get("/me")
def list_my_blocks(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    blocks = crud_block.list_my_blocks(db, current.id)
    result = []
    for block in blocks:
        result.append({
            "id": block.id,
            "blocker_id": block.blocker_id,
            "blocked_id": block.blocked_id,
            "created_at": block.created_at.isoformat() if block.created_at else None,
            "blocked_user": {
                "id": block.blocked.id,
                "nickname": block.blocked.nickname,
                "avatar": block.blocked.avatar or "🐱",
            },
        })
    return result