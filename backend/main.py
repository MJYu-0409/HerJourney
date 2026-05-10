import json
import os
from datetime import date, timedelta, datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, SessionLocal, Base
from models import User, Post
from config import MOCK_USER_ID, UPLOAD_DIR
from routers import user, survey, chat, profile, report, community

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="HerJourney API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(user.router)
app.include_router(survey.router)
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(report.router)
app.include_router(community.router)


# ── Startup: init DB + seed mock data ────────────────────────────────────────

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    _migrate_columns()
    _seed_mock_data()


def _migrate_columns():
    """Add new columns to existing tables without full migration framework."""
    from sqlalchemy import text
    migrations = [
        "ALTER TABLE daily_surveys ADD COLUMN medication JSON",
        "ALTER TABLE daily_surveys ADD COLUMN weekly_data JSON",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception:
                pass  # Column already exists


_SYMPTOM_KEY_MAP = {
    "palpitations":          "palpitation",
    "irritability":          "mood_swing",
    "sleep_onset_difficulty":"sleep_onset",
    "nighttime_awakening":   "sleep_wake",
    "early_awakening":       "early_wake",
    "poor_concentration":    "concentration",
    "recurrent_uti":         "uti",
    "joint_muscle_pain":     "joint_pain",
}

_FLOW_MAP = {"少": 1, "中": 2, "多": 3}
_STATUS_MAP = {"ongoing": "period", "ended_this_cycle": "none"}
_WEIGHT_MAP = {"无变化": "stable", "增加": "increase", "减少": "decrease"}
_BP_MAP     = {"正常": "normal", "偏低": "low", "偏高": "high", "高": "very_high"}


def _normalize_symptoms(raw: dict, all_keys: list[str]) -> dict[str, int]:
    out = {k: 0 for k in all_keys}
    for k, v in raw.items():
        canonical = _SYMPTOM_KEY_MAP.get(k, k)
        if canonical in out:
            out[canonical] = int(v)
    return out


def _normalize_weekly(raw_str) -> dict | None:
    if not raw_str:
        return None
    try:
        w = json.loads(raw_str) if isinstance(raw_str, str) else raw_str
    except Exception:
        return None
    out = {}
    wc = w.get("weight_change")
    if wc:
        out["weight"] = _WEIGHT_MAP.get(wc, "stable")
    bp = w.get("blood_pressure")
    if bp:
        out["bp"] = _BP_MAP.get(bp, "normal")
    joint = w.get("persistent_joint_pain")
    if joint is not None:
        out["joint"] = bool(joint)
    libido = w.get("sexual_discomfort")
    if libido is not None:
        out["libido"] = "yes" if libido else "no"
    return out or None


def _seed_surveys_from_json(db, path: str):
    from models import DailySurvey
    from constants import SYMPTOM_KEYS

    with open(path, encoding="utf-8") as f:
        records = json.load(f)

    for r in records:
        survey_date = date.fromisoformat(r["survey_date"])

        raw_symptoms = r.get("symptoms", {})
        if isinstance(raw_symptoms, str):
            try:
                raw_symptoms = json.loads(raw_symptoms)
            except Exception:
                raw_symptoms = {}
        symptoms = _normalize_symptoms(raw_symptoms, SYMPTOM_KEYS)

        raw_status = r.get("menstrual_status", "none")
        menstrual_status = _STATUS_MAP.get(raw_status, raw_status)

        raw_flow = r.get("menstrual_flow")
        menstrual_flow = _FLOW_MAP.get(raw_flow) if isinstance(raw_flow, str) else raw_flow

        raw_abnormal = r.get("menstrual_abnormal")
        if not raw_abnormal or raw_abnormal == "无":
            menstrual_abnormal = None
        elif isinstance(raw_abnormal, list):
            menstrual_abnormal = raw_abnormal
        else:
            menstrual_abnormal = [raw_abnormal]

        raw_med = r.get("medication")
        if not raw_med or raw_med == "无":
            medication = None
        elif isinstance(raw_med, list):
            medication = raw_med
        else:
            medication = [raw_med]

        weekly_data = _normalize_weekly(r.get("weekly_supplement"))

        survey = DailySurvey(
            user_id=MOCK_USER_ID,
            survey_date=survey_date,
            menstrual_status=menstrual_status,
            menstrual_day=r.get("menstrual_day"),
            menstrual_flow=menstrual_flow,
            menstrual_pain=r.get("menstrual_pain"),
            menstrual_abnormal=menstrual_abnormal,
            symptoms=symptoms,
            overall_score=r.get("overall_score"),
            medication=medication,
            weekly_data=weekly_data,
            notes=r.get("notes"),
        )
        db.add(survey)


def _seed_surveys_random(db):
    import random
    from models import DailySurvey
    from constants import SYMPTOM_KEYS
    random.seed(42)
    active_keys = ["hot_flash", "night_sweat", "sleep_onset", "sleep_wake", "mood_swing", "fatigue"]
    for i in range(30, 0, -1):
        d = date.today() - timedelta(days=i)
        active = {k: random.randint(1, 5) for k in active_keys}
        survey = DailySurvey(
            user_id=MOCK_USER_ID,
            survey_date=d,
            menstrual_status="none",
            symptoms={**{k: 0 for k in SYMPTOM_KEYS}, **active},
            overall_score=random.randint(2, 4),
        )
        db.add(survey)


def _seed_mock_data():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.id == MOCK_USER_ID).first():
            return  # already seeded

        mock_user = User(
            id=MOCK_USER_ID,
            nickname="小桃",
            birth_year=1972,
            menopause_stage="perimenopause",
        )
        db.add(mock_user)

        # Load 90-day sample surveys from JSON file
        sample_path = os.path.join(os.path.dirname(__file__), "..", "mock_data", "survey_enhanced_90d.json")
        if os.path.exists(sample_path):
            _seed_surveys_from_json(db, sample_path)
        else:
            _seed_surveys_random(db)

        # 2 official posts
        official_posts = [
            Post(
                user_id=None,
                post_type="official",
                title="【科普】围绝经期潮热，你需要知道的一切",
                content=(
                    "潮热是围绝经期最常见的症状之一，影响约75%的女性。它是由于雌激素水平下降，"
                    "导致下丘脑体温调节中枢功能紊乱引起的。\n\n"
                    "**为什么会出现潮热？**\n"
                    "雌激素下降→下丘脑误判体温偏高→启动散热机制→血管扩张→热感、出汗。\n\n"
                    "**如何应对？**\n"
                    "1. 穿着透气棉质衣物，随身携带小风扇\n"
                    "2. 避免触发因素：辛辣食物、咖啡因、酒精\n"
                    "3. 规律有氧运动可减少发作频率\n"
                    "4. 严重时可咨询医生了解激素替代疗法\n\n"
                    "记住，你不是一个人在经历这一切。🌸"
                ),
                tags=["#潮热", "#科普", "#HerJourney", "#官方"],
                is_ai_generated=False,
                status="published",
                published_at=datetime.utcnow() - timedelta(days=5),
            ),
            Post(
                user_id=None,
                post_type="official",
                title="【官方】HerJourney 使用指南——让每一天都被记录",
                content=(
                    "欢迎来到 HerJourney！这里是专属于围绝经期女性的温暖社区。\n\n"
                    "**四大功能助你走过这段旅程：**\n\n"
                    "📋 **每日问卷** — 花2分钟记录今天的症状，数据越多，AI越懂你。\n\n"
                    "💬 **AI问答** — 有任何疑问都可以问，我们的AI伴侣随时在线，"
                    "既懂医学知识，也懂你的感受。\n\n"
                    "📊 **个人主页** — 查看你的健康趋势，生成专属经验贴和症状报告。\n\n"
                    "🌺 **社区** — 分享你的经历，也从姐妹们的经验中汲取力量。\n\n"
                    "更年期不是终点，而是新的开始。我们陪你一起走。❤️"
                ),
                tags=["#HerJourney", "#使用指南", "#官方"],
                is_ai_generated=False,
                status="published",
                published_at=datetime.utcnow() - timedelta(days=10),
            ),
        ]
        for p in official_posts:
            db.add(p)

        db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "HerJourney API is running", "docs": "/docs"}


@app.get("/api/diag/qwen")
def diag_qwen():
    """Temporary endpoint to test Qwen API connectivity."""
    try:
        from services.qwen import chat_completion
        result = chat_completion([{"role": "user", "content": "说\"ok\""}], max_tokens=10)
        return {"status": "ok", "response": result}
    except Exception as e:
        return {"status": "error", "error": type(e).__name__, "message": str(e)}
