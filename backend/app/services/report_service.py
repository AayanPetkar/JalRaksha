import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from geoalchemy2.elements import WKTElement
from app.models.user import User
from app.models.report import CitizenReport
from app.schemas.report import CitizenReportCreate, CitizenReportOut


def create_citizen_report(db: Session, user: User, data: CitizenReportCreate) -> CitizenReportOut:
    point_wkt = f"POINT({data.longitude} {data.latitude})"
    report = CitizenReport(
        user_id=user.id,
        latitude=data.latitude,
        longitude=data.longitude,
        location=WKTElement(point_wkt, srid=4326),
        description=data.description,
        disaster_category=data.disaster_category,
        photo_url=data.photo_url,
        voice_note_url=data.voice_note_url,
        verification_status="UNVERIFIED",
        source_tag="CITIZEN_REPORT",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return CitizenReportOut.model_validate(report)


def list_reports(db: Session, limit: int = 50) -> List[CitizenReportOut]:
    reports = (
        db.query(CitizenReport)
        .order_by(CitizenReport.created_at.desc())
        .limit(limit)
        .all()
    )
    return [CitizenReportOut.model_validate(r) for r in reports]


def verify_citizen_report(db: Session, report_id: uuid.UUID) -> CitizenReportOut:
    report = db.query(CitizenReport).filter(CitizenReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen report not found."
        )
    report.verification_status = "VERIFIED"
    db.commit()
    db.refresh(report)
    return CitizenReportOut.model_validate(report)
