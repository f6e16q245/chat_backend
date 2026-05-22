from sqlalchemy.orm import Session
from app.models.report import Report
from app.schemas.report import ReportCreate


def create_report(db: Session, reporter_id: int, data: ReportCreate) -> Report:
    report = Report(
        reporter_id=reporter_id,
        reported_id=data.reported_id,
        reason=data.reason,
        detail=data.detail,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_my_reports(db: Session, reporter_id: int) -> list[Report]:
    return (
        db.query(Report)
        .filter(Report.reporter_id == reporter_id)
        .order_by(Report.created_at.desc())
        .all()
    )


def count_reports_against(db: Session, user_id: int) -> int:
    """특정 유저가 받은 총 신고 수 (제재 로직에서 사용 예정)"""
    return db.query(Report).filter(Report.reported_id == user_id).count()