import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.flood import FloodRisk, RiskFactor
from app.schemas.flood import FloodRiskOut, FloodImpactOut, FloodRiskWhyOut, RiskFactorOut

DEMO_RISK_ID = uuid.UUID("66666666-6666-6666-6666-666666666602")
DEMO_VILLAGE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def _risk_factors_for(db: Session, risk_id: uuid.UUID) -> List[RiskFactorOut]:
    factors = (
        db.query(RiskFactor)
        .filter(RiskFactor.flood_risk_id == risk_id)
        .order_by(RiskFactor.contribution_percentage.desc())
        .all()
    )
    return [RiskFactorOut.model_validate(f) for f in factors]


def get_current_flood_risk(db: Session, latitude: float = 19.0760, longitude: float = 72.8777) -> FloodRiskOut:
    risk = db.query(FloodRisk).filter(FloodRisk.id == DEMO_RISK_ID).first()
    if not risk:
        # Fallback synthetic demo record. In practice the Phase A demo seed
        # always creates this row on startup, so this path should not be hit
        # in the demo runtime; it exists only as a defensive default.
        return FloodRiskOut(
            id=DEMO_RISK_ID,
            village_id=DEMO_VILLAGE_ID,
            village_name="Kurla, Mumbai",
            risk_score=20.0,
            risk_level="LOW",
            confidence_score=0.80,
            data_freshness_minutes=5,
            source_tag="SIMULATED_DEMO_DATA",
            is_demo_data=True,
            disclaimer="AI prediction; not an official government warning.",
            local_impact=FloodImpactOut(),
            main_risk_factors=[],
            evaluated_at=datetime.now(timezone.utc)
        )

    main_risk_factors = _risk_factors_for(db, risk.id)
    evaluated_at = risk.evaluated_at
    if evaluated_at and evaluated_at.tzinfo is None:
        # SQLite does not preserve timezone-awareness on stored values;
        # everything is written as UTC, so label it back as such.
        evaluated_at = evaluated_at.replace(tzinfo=timezone.utc)

    return FloodRiskOut(
        id=risk.id,
        village_id=risk.village_id,
        village_name="Kurla Rural",
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        confidence_score=risk.confidence_score,
        data_freshness_minutes=risk.data_freshness_minutes,
        source_tag=risk.source_tag,
        is_demo_data=(risk.source_tag == "SIMULATED_DEMO_DATA"),
        disclaimer="AI prediction; not an official government warning.",
        local_impact=FloodImpactOut(
            affected_houses_count=risk.affected_houses_count,
            affected_farmland_acres=risk.affected_farmland_acres,
            affected_schools_count=risk.affected_schools_count,
            affected_hospitals_count=risk.affected_hospitals_count
        ),
        main_risk_factors=main_risk_factors,
        evaluated_at=evaluated_at
    )


def get_risk_why_explanation(db: Session, risk_id: uuid.UUID = DEMO_RISK_ID) -> FloodRiskWhyOut:
    """Returns the current contributing risk factors for a flood-risk record.

    Reads live from the database (the seeded baseline, or whatever the
    admin simulation endpoints have most recently written) rather than
    inventing/hardcoding values, per the SIH demo scope's data-honesty rule.
    """
    risk = db.query(FloodRisk).filter(FloodRisk.id == risk_id).first()
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flood risk record not found. Ensure the demo database has been seeded."
        )

    factors = _risk_factors_for(db, risk.id)

    if risk.evaluated_at:
        evaluated_at = risk.evaluated_at
        if evaluated_at.tzinfo is None:
            # SQLite does not preserve timezone-awareness on DateTime(timezone=True)
            # columns; the value was always written as UTC, so treat it as such.
            evaluated_at = evaluated_at.replace(tzinfo=timezone.utc)
        minutes_ago = max(0, int((datetime.now(timezone.utc) - evaluated_at).total_seconds() // 60))
        data_updated = "just now" if minutes_ago == 0 else f"{minutes_ago} minute{'s' if minutes_ago != 1 else ''} ago"
    else:
        data_updated = f"{risk.data_freshness_minutes} minutes ago"

    return FloodRiskWhyOut(
        risk_id=risk.id,
        village_id=risk.village_id,
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        confidence="High" if risk.confidence_score >= 0.8 else "Moderate",
        data_updated=data_updated,
        source_tag=risk.source_tag,
        contributing_factors=factors
    )
