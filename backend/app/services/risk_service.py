import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.flood import FloodRisk, RiskFactor
from app.schemas.flood import FloodRiskOut, FloodImpactOut, FloodRiskWhyOut, RiskFactorOut

DEMO_RISK_ID = uuid.UUID("66666666-6666-6666-6666-666666666602")
DEMO_VILLAGE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

def get_current_flood_risk(db: Session, latitude: float = 19.0760, longitude: float = 72.8777) -> FloodRiskOut:
    risk = db.query(FloodRisk).filter(FloodRisk.id == DEMO_RISK_ID).first()
    if not risk:
        # Fallback synthetic demo record
        return FloodRiskOut(
            id=DEMO_RISK_ID,
            village_id=DEMO_VILLAGE_ID,
            village_name="Sangli Rural",
            risk_score=84.0,
            risk_level="CRITICAL",
            confidence_score=0.92,
            data_freshness_minutes=7,
            source_tag="SIMULATED_DEMO_DATA",
            disclaimer="AI prediction; not an official government warning.",
            local_impact=FloodImpactOut(
                affected_houses_count=320,
                affected_farmland_acres=185.0,
                affected_schools_count=1,
                affected_hospitals_count=0
            ),
            evaluated_at=datetime.now(timezone.utc)
        )
    
    return FloodRiskOut(
        id=risk.id,
        village_id=risk.village_id,
        village_name="Sangli Rural",
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        confidence_score=risk.confidence_score,
        data_freshness_minutes=risk.data_freshness_minutes,
        source_tag=risk.source_tag,
        disclaimer="AI prediction; not an official government warning.",
        local_impact=FloodImpactOut(
            affected_houses_count=risk.affected_houses_count,
            affected_farmland_acres=risk.affected_farmland_acres,
            affected_schools_count=risk.affected_schools_count,
            affected_hospitals_count=risk.affected_hospitals_count
        ),
        evaluated_at=risk.evaluated_at
    )


def get_risk_why_explanation(db: Session, risk_id: uuid.UUID) -> FloodRiskWhyOut:
    factors = [
        RiskFactorOut(
            factor_key="HEAVY_RAINFALL",
            contribution_percentage=42.0,
            description_en="Forecasted heavy rainfall (125mm in 24h)",
            description_mr="मुसळधार पावसाचा अंदाज (24 तासात 125 मिमी)",
            description_hi="भारी बारिश का अनुमान (24 घंटे में 125 मिमी)"
        ),
        RiskFactorOut(
            factor_key="RIVER_LEVEL",
            contribution_percentage=30.0,
            description_en="Rising river water level near Krishna basin (4.2m)",
            description_mr="कृष्णा पात्राजवळ नदीची वाढती पातळी (4.2 मी)",
            description_hi="कृष्णा बेसिन के पास नदी का बढ़ता जलस्तर (4.2 मी)"
        ),
        RiskFactorOut(
            factor_key="SOIL_SATURATION",
            contribution_percentage=18.0,
            description_en="High soil moisture saturation (88.5%)",
            description_mr="जमिनीची जास्त पाझर क्षमता (88.5%)",
            description_hi="उच्च मृदा नमी संतृप्ति (88.5%)"
        ),
        RiskFactorOut(
            factor_key="LOW_ELEVATION",
            contribution_percentage=10.0,
            description_en="Location in low-lying river basin terrain",
            description_mr="सखल भौगोलिक नदीपात्र स्थान",
            description_hi="निचले नदी बेसिन क्षेत्र में स्थिति"
        )
    ]
    return FloodRiskWhyOut(
        risk_id=risk_id,
        village_id=DEMO_VILLAGE_ID,
        risk_score=84.0,
        risk_level="CRITICAL",
        confidence="High",
        data_updated="7 minutes ago",
        source_tag="SIMULATED_DEMO_DATA",
        contributing_factors=factors
    )
