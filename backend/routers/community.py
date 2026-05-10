import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import Post, User
from schemas import (
    ShareIn, ShareOut,
    PostListOut, PostSummary, PostDetailOut,
    LikeOut, TagsOut, TagCount, UploadOut,
)
from config import MOCK_USER_ID, UPLOAD_DIR

router = APIRouter(prefix="/api", tags=["community"])


def _user_id(x_user_id: str = Header(default=MOCK_USER_ID)) -> str:
    return x_user_id


def _nickname(user_id: str, db: Session) -> str:
    if user_id is None:
        return "官方账号"
    u = db.query(User).filter(User.id == user_id).first()
    return u.nickname if u else "匿名姐妹"


# ── Share ──────────────────────────────────────────────────────────────────────

@router.post("/community/share", response_model=ShareOut, status_code=201)
def share_post(body: ShareIn, db: Session = Depends(get_db), uid: str = Depends(_user_id)):
    now = datetime.utcnow()
    if body.post_id:
        post = db.query(Post).filter(Post.id == body.post_id, Post.user_id == uid).first()
        if not post:
            raise HTTPException(
                status_code=404,
                detail={"error": "NOT_FOUND", "message": "草稿不存在或无权操作"},
            )
        post.title = body.title
        post.content = body.content
        post.tags = body.tags
        post.status = "published"
        post.published_at = now
    else:
        post = Post(
            user_id=uid,
            post_type=body.post_type,
            title=body.title,
            content=body.content,
            tags=body.tags,
            is_ai_generated=False,
            status="published",
            published_at=now,
        )
        db.add(post)

    db.commit()
    db.refresh(post)
    return ShareOut(post_id=post.id, status="published", published_at=now)


# ── Post list ──────────────────────────────────────────────────────────────────

@router.get("/community/posts", response_model=PostListOut)
def list_posts(
    tab: str = "all",
    keyword: str | None = None,
    tag: str | None = None,
    page: int = 1,
    page_size: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(Post).filter(Post.status == "published")

    if tab != "all":
        q = q.filter(Post.post_type == tab)

    if keyword:
        q = q.filter(or_(Post.title.ilike(f"%{keyword}%"), Post.content.ilike(f"%{keyword}%")))

    if tag:
        # JSON contains check: works in SQLite and PostgreSQL
        q = q.filter(Post.tags.contains([tag]))

    total = q.count()

    # Official posts first, then by published_at desc
    posts = (
        q.order_by(Post.user_id.is_(None).desc(), Post.published_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        PostSummary(
            id=p.id,
            post_type=p.post_type,
            title=p.title,
            summary=(p.content or "")[:80],
            tags=p.tags or [],
            author_nickname=_nickname(p.user_id, db),
            is_official=p.user_id is None,
            likes=p.likes,
            views=p.views,
            published_at=p.published_at,
        )
        for p in posts
    ]
    return PostListOut(total=total, page=page, items=items)


# ── Post detail ───────────────────────────────────────────────────────────────

@router.get("/community/posts/{post_id}", response_model=PostDetailOut)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id, Post.status == "published").first()
    if not post:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "帖子不存在"},
        )
    post.views += 1
    db.commit()
    return PostDetailOut(
        id=post.id,
        post_type=post.post_type,
        title=post.title,
        content=post.content,
        tags=post.tags or [],
        report_data=post.report_data,
        author_nickname=_nickname(post.user_id, db),
        is_official=post.user_id is None,
        likes=post.likes,
        views=post.views,
        published_at=post.published_at,
    )


# ── Like ──────────────────────────────────────────────────────────────────────

@router.post("/community/posts/{post_id}/like", response_model=LikeOut)
def like_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id, Post.status == "published").first()
    if not post:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "帖子不存在"})
    post.likes += 1
    db.commit()
    return LikeOut(likes=post.likes)


# ── Tags ──────────────────────────────────────────────────────────────────────

@router.get("/community/tags", response_model=TagsOut)
def get_tags(limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(Post.tags).filter(Post.status == "published").all()
    counter: dict[str, int] = {}
    for (tags,) in posts:
        for tag in (tags or []):
            counter[tag] = counter.get(tag, 0) + 1
    sorted_tags = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:limit]
    return TagsOut(tags=[TagCount(name=t, count=c) for t, c in sorted_tags])


# ── Upload ────────────────────────────────────────────────────────────────────

@router.post("/post/upload", response_model=UploadOut)
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    dest = os.path.join(UPLOAD_DIR, filename)
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    file_type = "image" if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"} else "audio"
    return UploadOut(url=f"/static/uploads/{filename}", type=file_type)
