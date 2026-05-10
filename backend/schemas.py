from __future__ import annotations
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from constants import SYMPTOM_KEYS


# ── User ──────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    nickname: str
    menopause_stage: str
    birth_year: Optional[int] = None

    model_config = {"from_attributes": True}


# ── Survey ────────────────────────────────────────────────────────────────────

class SurveyIn(BaseModel):
    menstrual_status: str = "none"
    menstrual_day: Optional[int] = None
    menstrual_flow: Optional[int] = None
    menstrual_pain: Optional[int] = None
    menstrual_abnormal: Optional[list[str]] = None
    symptoms: dict[str, int] = Field(default_factory=dict)
    overall_score: Optional[int] = Field(None, ge=1, le=5)
    medication: Optional[list[str]] = None
    weekly_data: Optional[dict] = None
    notes: Optional[str] = None

    def full_symptoms(self) -> dict[str, int]:
        base = {k: 0 for k in SYMPTOM_KEYS}
        base.update({k: v for k, v in self.symptoms.items() if k in SYMPTOM_KEYS})
        return base


class SurveySubmitOut(BaseModel):
    id: str
    survey_date: date
    message: str


class SurveyTodayOut(BaseModel):
    completed: bool
    survey_date: Optional[date] = None
    overall_score: Optional[int] = None


class SurveyRecord(BaseModel):
    survey_date: date
    overall_score: Optional[int]
    symptoms: dict[str, int]
    menstrual_status: str
    medication: Optional[list[str]] = None
    weekly_data: Optional[dict] = None

    model_config = {"from_attributes": True}


class SurveyHistoryOut(BaseModel):
    records: list[SurveyRecord]


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatIn(BaseModel):
    session_id: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageOut(BaseModel):
    session_id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionSummary(BaseModel):
    session_id: str
    first_message: str
    message_count: int
    last_at: datetime


class ChatSessionsOut(BaseModel):
    sessions: list[SessionSummary]


class ChatHistoryOut(BaseModel):
    session_id: str
    messages: list[dict[str, Any]]


# ── Profile stats ─────────────────────────────────────────────────────────────

class SymptomStat(BaseModel):
    key: str
    name: str
    avg_score: float
    days_reported: int


class ProfileStatsOut(BaseModel):
    total_checkin_days: int
    current_streak: int
    total_ai_chats: int
    avg_overall_score_30d: Optional[float]
    top_symptoms: list[SymptomStat]


# ── Reports ───────────────────────────────────────────────────────────────────

class DataPoint(BaseModel):
    date: date
    score: int


class SymptomSeries(BaseModel):
    key: str
    name: str
    data_points: list[DataPoint]
    avg_score: float
    days_reported: int
    trend: str  # improving / worsening / stable


class ReportChartOut(BaseModel):
    since: Optional[date]
    until: date
    symptoms: list[SymptomSeries]


class ReportGenerateIn(BaseModel):
    days: int = Field(90, ge=0, le=3650)
    symptom_keys: list[str] = Field(default_factory=list)


class ReportGenerateOut(BaseModel):
    post_id: str
    days: int
    symptom_keys: list[str]
    symptoms: list[SymptomSeries]
    interpretation: str
    tags: list[str]
    status: str


class DraftItem(BaseModel):
    post_id: str
    post_type: str
    title: str
    created_at: datetime


class DraftsOut(BaseModel):
    drafts: list[DraftItem]


# ── Community ─────────────────────────────────────────────────────────────────

class ShareIn(BaseModel):
    post_id: Optional[str] = None
    post_type: str = "report"
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class ShareOut(BaseModel):
    post_id: str
    status: str
    published_at: datetime


class PostSummary(BaseModel):
    id: str
    post_type: str
    title: str
    summary: str
    tags: list[str]
    author_nickname: str
    is_official: bool
    likes: int
    views: int
    published_at: Optional[datetime]


class PostListOut(BaseModel):
    total: int
    page: int
    items: list[PostSummary]


class PostDetailOut(BaseModel):
    id: str
    post_type: str
    title: str
    content: str
    tags: list[str]
    report_data: Optional[Any]
    author_nickname: str
    is_official: bool
    likes: int
    views: int
    published_at: Optional[datetime]


class LikeOut(BaseModel):
    likes: int


class TagCount(BaseModel):
    name: str
    count: int


class TagsOut(BaseModel):
    tags: list[TagCount]


class UploadOut(BaseModel):
    url: str
    type: str


# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorOut(BaseModel):
    error: str
    message: str
    status_code: int
