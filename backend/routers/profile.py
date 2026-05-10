from datetime import date, timedelta
from fastapi import APIRouter, Depends, Header
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import DailySurvey, ChatMessage
from schemas import ProfileStatsOut, SymptomStat
from services.report_builder import aggregate_symptoms, calc_streak
from constants import SYMPTOM_NAMES_ZH
from config import MOCK_USER_ID

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _user_id(x_user_id: str = Header(default=MOCK_USER_ID)) -> str:
    return x_user_id


@router.get("/stats", response_model=ProfileStatsOut)
def get_stats(db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    all_surveys = db.query(DailySurvey).filter(DailySurvey.user_id == uid).all()
    total_checkin = len({s.survey_date for s in all_surveys})
    streak = calc_streak(all_surveys)

    total_chats = (
        db.query(func.count(ChatMessage.id))
        .filter(ChatMessage.user_id == uid, ChatMessage.role == "user")
        .scalar()
        or 0
    )

    since_30 = date.today() - timedelta(days=30)
    surveys_30d = [s for s in all_surveys if s.survey_date >= since_30]
    scored = [s.overall_score for s in surveys_30d if s.overall_score]
    avg_score_30d = round(sum(scored) / len(scored), 1) if scored else None

    aggregated = aggregate_symptoms(surveys_30d)
    top_symptoms = [
        SymptomStat(
            key=item["key"],
            name=item["name"],
            avg_score=item["avg_score"],
            days_reported=item["days_reported"],
        )
        for item in aggregated[:5]
    ]

    return ProfileStatsOut(
        total_checkin_days=total_checkin,
        current_streak=streak,
        total_ai_chats=total_chats,
        avg_overall_score_30d=avg_score_30d,
        top_symptoms=top_symptoms,
    )
