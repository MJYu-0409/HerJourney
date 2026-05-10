import os
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserOut, UserUpdate
from config import MOCK_USER_ID, UPLOAD_DIR

router = APIRouter(prefix="/api/user", tags=["user"])


def get_current_user_id(x_user_id: str = MOCK_USER_ID) -> str:
    return x_user_id


@router.get("/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == MOCK_USER_ID).first()
    return user


@router.put("/me", response_model=UserOut)
def update_me(body: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == MOCK_USER_ID).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.birth_year is not None:
        user.birth_year = body.birth_year
    if body.menopause_stage is not None:
        user.menopause_stage = body.menopause_stage
    db.commit()
    db.refresh(user)
    return user


@router.post("/avatar", response_model=UserOut)
def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == MOCK_USER_ID).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        raise HTTPException(status_code=400, detail="Only .jpg .jpeg .png .webp allowed")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    user.avatar_url = f"/static/uploads/{filename}"
    db.commit()
    db.refresh(user)
    return user
