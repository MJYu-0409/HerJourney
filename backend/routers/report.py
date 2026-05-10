from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import DailySurvey, Post
from schemas import (
    ReportChartOut, SymptomSeries, DataPoint,
    ReportGenerateIn, ReportGenerateOut,
    DraftsOut, DraftItem,
)
from services.qwen import generate_report_interpretation
from services.report_builder import (
    build_symptom_series, build_prompt_blocks,
    build_tags, build_report_title,
)
from constants import SYMPTOM_KEYS
from config import MOCK_USER_ID

router = APIRouter(prefix="/api/report", tags=["report"])


def _user_id(x_user_id: str = Header(default=MOCK_USER_ID)) -> str:
    return x_user_id


def _load_surveys(db: Session, uid: str, days: int) -> tuple[list[DailySurvey], date | None]:
    """Returns (surveys, since_date). days=0 means all history."""
    q = db.query(DailySurvey).filter(DailySurvey.user_id == uid)
    if days > 0:
        since = date.today() - timedelta(days=days)
        q = q.filter(DailySurvey.survey_date >= since)
    else:
        since = None
    return q.order_by(DailySurvey.survey_date.asc()).all(), since


def _series_to_schema(item: dict) -> SymptomSeries:
    return SymptomSeries(
        key=item["key"],
        name=item["name"],
        data_points=[DataPoint(date=d, score=s) for d, s in item["data_points"]],
        avg_score=item["avg_score"],
        days_reported=item["days_reported"],
        trend=item["trend"],
    )


# ── Chart data (no AI) ────────────────────────────────────────────────────────

@router.get("/chart", response_model=ReportChartOut)
def get_chart(
    days: int = Query(default=90, ge=0),
    symptoms: str | None = Query(default=None, description="逗号分隔的症状 key，不传=全部"),
    db: Session = Depends(get_db),
    uid: str = Depends(_user_id),
):
    filter_keys = None
    if symptoms:
        filter_keys = [k.strip() for k in symptoms.split(",") if k.strip() in SYMPTOM_KEYS]

    surveys, since = _load_surveys(db, uid, days)
    series_list = build_symptom_series(surveys, filter_keys)

    return ReportChartOut(
        since=since,
        until=date.today(),
        symptoms=[_series_to_schema(item) for item in series_list],
    )


# ── Generate report (with AI) ─────────────────────────────────────────────────

@router.post("/generate", response_model=ReportGenerateOut, status_code=201)
def generate_report(
    body: ReportGenerateIn,
    db: Session = Depends(get_db),
    uid: str = Depends(_user_id),
):
    filter_keys = [k for k in body.symptom_keys if k in SYMPTOM_KEYS] or None

    surveys, _ = _load_surveys(db, uid, body.days)
    if not surveys:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "所选时间段内无问卷记录"},
        )

    series_list = build_symptom_series(surveys, filter_keys)
    if not series_list:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "所选症状在该时间段内无记录"},
        )

    prompt_blocks = build_prompt_blocks(series_list)
    try:
        interpretation = generate_report_interpretation(prompt_blocks, body.days)
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error": "QWEN_API_ERROR", "message": str(e)})

    tags = build_tags(series_list)
    title = build_report_title(series_list, body.days)
    used_keys = [item["key"] for item in series_list]

    report_data = {
        "days": body.days,
        "symptom_keys": used_keys,
        "series": [
            {
                "key": item["key"],
                "name": item["name"],
                "data_points": [{"date": str(d), "score": s} for d, s in item["data_points"]],
                "avg_score": item["avg_score"],
                "days_reported": item["days_reported"],
                "trend": item["trend"],
            }
            for item in series_list
        ],
    }

    post = Post(
        user_id=uid,
        post_type="report",
        title=title,
        content=interpretation,
        tags=tags,
        report_data=report_data,
        is_ai_generated=True,
        status="draft",
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return ReportGenerateOut(
        post_id=post.id,
        days=body.days,
        symptom_keys=used_keys,
        symptoms=[_series_to_schema(item) for item in series_list],
        interpretation=interpretation,
        tags=tags,
        status="draft",
    )


# ── Drafts ────────────────────────────────────────────────────────────────────

@router.get("/drafts", response_model=DraftsOut)
def list_drafts(db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    drafts = (
        db.query(Post)
        .filter(Post.user_id == uid, Post.status == "draft")
        .order_by(Post.created_at.desc())
        .all()
    )
    return DraftsOut(
        drafts=[
            DraftItem(post_id=p.id, post_type=p.post_type, title=p.title, created_at=p.created_at)
            for p in drafts
        ]
    )
