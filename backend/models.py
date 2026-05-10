import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, SmallInteger, Boolean,
    Date, DateTime, Text, JSON, ForeignKey, UniqueConstraint,
)
from database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    openid = Column(String(64), unique=True, nullable=True)
    nickname = Column(String(50), default="匿名姐妹")
    birth_year = Column(SmallInteger, nullable=True)
    menopause_stage = Column(String(20), default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)


class DailySurvey(Base):
    __tablename__ = "daily_surveys"
    __table_args__ = (UniqueConstraint("user_id", "survey_date", name="uq_user_date"),)

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    survey_date = Column(Date, nullable=False)
    menstrual_status = Column(String(20), default="none")
    menstrual_day = Column(SmallInteger, nullable=True)
    menstrual_flow = Column(SmallInteger, nullable=True)
    menstrual_pain = Column(SmallInteger, nullable=True)
    menstrual_abnormal = Column(JSON, nullable=True)
    symptoms = Column(JSON, nullable=False, default=dict)
    overall_score = Column(SmallInteger, nullable=True)
    medication = Column(JSON, nullable=True)
    weekly_data = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), nullable=False, index=True)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Post(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    post_type = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True, default=list)
    report_data = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    is_ai_generated = Column(Boolean, default=False)
    status = Column(String(10), default="draft")
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
