from datetime import date, timedelta
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database import get_db
from models import DailySurvey
from schemas import SurveyIn, SurveySubmitOut, SurveyTodayOut, SurveyHistoryOut, SurveyRecord
from config import MOCK_USER_ID

router = APIRouter(prefix="/api/survey", tags=["survey"])


def _user_id(x_user_id: str = Header(default=MOCK_USER_ID)) -> str:
    return x_user_id


@router.post("", response_model=SurveySubmitOut, status_code=201)
def submit_survey(body: SurveyIn, db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    today = date.today()
    existing = (
        db.query(DailySurvey)
        .filter(DailySurvey.user_id == uid, DailySurvey.survey_date == today)
        .first()
    )
    if existing:
        existing.menstrual_status = body.menstrual_status
        existing.menstrual_day = body.menstrual_day
        existing.menstrual_flow = body.menstrual_flow
        existing.menstrual_pain = body.menstrual_pain
        existing.menstrual_abnormal = body.menstrual_abnormal
        existing.symptoms = body.full_symptoms()
        existing.overall_score = body.overall_score
        existing.medication = body.medication
        existing.weekly_data = body.weekly_data
        existing.notes = body.notes
        db.commit()
        db.refresh(existing)
        return SurveySubmitOut(id=existing.id, survey_date=today, message="已更新今日打卡")
    else:
        record = DailySurvey(
            user_id=uid,
            survey_date=today,
            menstrual_status=body.menstrual_status,
            menstrual_day=body.menstrual_day,
            menstrual_flow=body.menstrual_flow,
            menstrual_pain=body.menstrual_pain,
            menstrual_abnormal=body.menstrual_abnormal,
            symptoms=body.full_symptoms(),
            overall_score=body.overall_score,
            medication=body.medication,
            weekly_data=body.weekly_data,
            notes=body.notes,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return SurveySubmitOut(id=record.id, survey_date=today, message="打卡成功")


@router.get("/today", response_model=SurveyTodayOut)
def get_today(db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    today = date.today()
    record = (
        db.query(DailySurvey)
        .filter(DailySurvey.user_id == uid, DailySurvey.survey_date == today)
        .first()
    )
    if not record:
        return SurveyTodayOut(completed=False)
    return SurveyTodayOut(completed=True, survey_date=today, overall_score=record.overall_score)


@router.get("/history", response_model=SurveyHistoryOut)
def get_history(days: int = 30, db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    days = max(1, min(days, 365))
    since = date.today() - timedelta(days=days)
    records = (
        db.query(DailySurvey)
        .filter(DailySurvey.user_id == uid, DailySurvey.survey_date >= since)
        .order_by(DailySurvey.survey_date.asc())
        .all()
    )
    return SurveyHistoryOut(
        records=[
            SurveyRecord(
                survey_date=r.survey_date,
                overall_score=r.overall_score,
                symptoms=r.symptoms or {},
                menstrual_status=r.menstrual_status or "none",
                medication=r.medication,
                weekly_data=r.weekly_data,
            )
            for r in records
        ]
    )
