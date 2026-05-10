from __future__ import annotations
from datetime import date, timedelta
from collections import defaultdict
from constants import SYMPTOM_KEYS, SYMPTOM_NAMES_ZH, SYMPTOM_TAGS_ZH
from models import DailySurvey, ChatMessage


# ── Chart data ────────────────────────────────────────────────────────────────

def build_symptom_series(
    surveys: list[DailySurvey],
    filter_keys: list[str] | None = None,
) -> list[dict]:
    """
    Build per-symptom time series from survey list.
    Returns list of dicts sorted by avg*days desc.
    filter_keys: if provided, only include those keys.
    """
    series: dict[str, list[tuple[date, int]]] = defaultdict(list)
    keys_to_use = filter_keys if filter_keys else SYMPTOM_KEYS

    for s in sorted(surveys, key=lambda x: x.survey_date):
        syms: dict = s.symptoms or {}
        for key in keys_to_use:
            score = syms.get(key, 0)
            if score > 0:
                series[key].append((s.survey_date, score))

    result = []
    for key, points in series.items():
        scores = [sc for _, sc in points]
        avg = round(sum(scores) / len(scores), 1)
        result.append(
            {
                "key": key,
                "name": SYMPTOM_NAMES_ZH.get(key, key),
                "tag": SYMPTOM_TAGS_ZH.get(key, f"#{key}"),
                "data_points": points,       # list of (date, int)
                "avg_score": avg,
                "days_reported": len(points),
                "trend": compute_trend(points),
            }
        )

    result.sort(key=lambda x: x["avg_score"] * x["days_reported"], reverse=True)
    return result


def build_prompt_blocks(series_list: list[dict]) -> list[dict]:
    """Convert series list to dicts suitable for qwen.generate_report_interpretation."""
    blocks = []
    for item in series_list:
        lines = [f"{d.isoformat()}: {s}分" for d, s in item["data_points"]]
        blocks.append(
            {
                "name": item["name"],
                "avg": item["avg_score"],
                "trend": item["trend"],
                "data_text": "\n".join(lines),
            }
        )
    return blocks


def build_tags(series_list: list[dict]) -> list[str]:
    tags = ["#HerJourney", "#健康报告"]
    for item in series_list[:4]:
        tag = item["tag"]
        if tag not in tags:
            tags.append(tag)
    return tags


def build_report_title(series_list: list[dict], days: int) -> str:
    if not series_list:
        return f"健康报告·近{days}天" if days else "健康报告·全部历史"
    names = "·".join(item["name"] for item in series_list[:3])
    period = f"近{days}天" if days else "全部历史"
    return f"健康报告·{names}·{period}"


# ── Trend / stats helpers ─────────────────────────────────────────────────────

def compute_trend(data_points: list[tuple[date, int]]) -> str:
    if len(data_points) < 3:
        return "stable"
    scores = [s for _, s in data_points]
    n = len(scores)
    mid = n // 2
    first_avg = sum(scores[:mid]) / mid
    second_avg = sum(scores[mid:]) / (n - mid)
    diff = second_avg - first_avg
    if diff <= -0.3:
        return "improving"
    if diff >= 0.3:
        return "worsening"
    return "stable"


def aggregate_symptoms(surveys: list[DailySurvey]) -> list[dict]:
    """Used by profile/stats — returns aggregated dicts without per-date points."""
    totals: dict[str, list[int]] = defaultdict(list)
    for s in surveys:
        syms: dict = s.symptoms or {}
        for key in SYMPTOM_KEYS:
            score = syms.get(key, 0)
            if score > 0:
                totals[key].append(score)

    result = []
    for key, scores in totals.items():
        avg = sum(scores) / len(scores)
        result.append(
            {
                "key": key,
                "name": SYMPTOM_NAMES_ZH.get(key, key),
                "tag": SYMPTOM_TAGS_ZH.get(key, f"#{key}"),
                "avg_score": round(avg, 1),
                "days_reported": len(scores),
            }
        )

    result.sort(key=lambda x: x["avg_score"] * x["days_reported"], reverse=True)
    return result


def calc_streak(surveys: list[DailySurvey]) -> int:
    if not surveys:
        return 0
    today = date.today()
    dates = sorted({s.survey_date for s in surveys}, reverse=True)
    streak = 0
    expected = today
    for d in dates:
        if d == expected:
            streak += 1
            expected = expected - timedelta(days=1)
        else:
            break
    return streak
