import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import ChatMessage
from schemas import ChatIn, ChatMessageOut, ChatSessionsOut, ChatHistoryOut, SessionSummary
from services.qwen import build_chat_messages, chat_completion
from config import MOCK_USER_ID

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _user_id(x_user_id: str = Header(default=MOCK_USER_ID)) -> str:
    return x_user_id


@router.post("", response_model=ChatMessageOut, status_code=201)
def send_message(body: ChatIn, db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    session_id = body.session_id or str(uuid.uuid4())

    history_rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in reversed(history_rows)]

    user_msg = ChatMessage(user_id=uid, session_id=session_id, role="user", content=body.content)
    db.add(user_msg)
    db.flush()

    try:
        messages = build_chat_messages(history, body.content)
        ai_content = chat_completion(messages)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=502, detail={"error": "QWEN_API_ERROR", "message": str(e)})

    ai_msg = ChatMessage(user_id=uid, session_id=session_id, role="assistant", content=ai_content)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ChatMessageOut(
        session_id=session_id,
        role="assistant",
        content=ai_content,
        created_at=ai_msg.created_at,
    )


@router.get("/sessions", response_model=ChatSessionsOut)
def list_sessions(db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    rows = (
        db.query(
            ChatMessage.session_id,
            func.count(ChatMessage.id).label("cnt"),
            func.max(ChatMessage.created_at).label("last_at"),
        )
        .filter(ChatMessage.user_id == uid)
        .group_by(ChatMessage.session_id)
        .order_by(func.max(ChatMessage.created_at).desc())
        .all()
    )

    sessions = []
    for row in rows:
        first = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == row.session_id, ChatMessage.role == "user")
            .order_by(ChatMessage.created_at.asc())
            .first()
        )
        sessions.append(
            SessionSummary(
                session_id=row.session_id,
                first_message=first.content[:50] if first else "",
                message_count=row.cnt,
                last_at=row.last_at,
            )
        )
    return ChatSessionsOut(sessions=sessions)


@router.get("/history", response_model=ChatHistoryOut)
def get_history(session_id: str, db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.user_id == uid)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return ChatHistoryOut(
        session_id=session_id,
        messages=[
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in msgs
        ],
    )
