from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserOut
from config import MOCK_USER_ID

router = APIRouter(prefix="/api/user", tags=["user"])


def get_current_user_id(x_user_id: str = MOCK_USER_ID) -> str:
    return x_user_id


@router.get("/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == MOCK_USER_ID).first()
    return user
