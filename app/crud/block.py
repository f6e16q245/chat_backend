from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.block import Block


def create_block(db: Session, blocker_id: int, blocked_id: int) -> Block | None:
    """이미 차단했으면 None 반환"""
    block = Block(blocker_id=blocker_id, blocked_id=blocked_id)
    db.add(block)
    try:
        db.commit()
        db.refresh(block)
        return block
    except IntegrityError:
        db.rollback()
        return None


def delete_block(db: Session, blocker_id: int, blocked_id: int) -> bool:
    """차단 해제. 차단 기록 있었으면 True, 없었으면 False"""
    result = (
        db.query(Block)
        .filter(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id)
        .delete()
    )
    db.commit()
    return result > 0


def list_my_blocks(db: Session, blocker_id: int) -> list[Block]:
    return (
        db.query(Block)
        .filter(Block.blocker_id == blocker_id)
        .order_by(Block.created_at.desc())
        .all()
    )


def get_blocked_user_ids(db: Session, user_id: int) -> set[int]:
    """내가 차단한 + 나를 차단한 유저 ID 모두 (매칭에서 양방향 제외용)"""
    blocked_by_me = db.query(Block.blocked_id).filter(Block.blocker_id == user_id).all()
    blocking_me = db.query(Block.blocker_id).filter(Block.blocked_id == user_id).all()
    return {b[0] for b in blocked_by_me} | {b[0] for b in blocking_me}