"""
生成个人症状趋势模拟数据（14~30天）

核心设计：数据必须有趋势性，不能是纯随机噪音。
围绝经期女性的症状通常呈现：
- 波动性（每天不完全一样）
- 趋势性（整体改善或恶化）
- 周期性（与月经周期相关）
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ============ 配置 ============
USER_ID = "mock-user-001"
DAYS = 21  # 3周数据，覆盖一个完整周期，视觉效果最好
OUTPUT_PATH = Path(__file__).parent.parent / "mock_data"

# 症状模块定义（与 PRD 对应）
SYMPTOM_MODULES = {
    "cardiovascular": ["hot_flash", "night_sweat", "palpitations", "chest_tightness"],
    "musculoskeletal": ["joint_stiffness", "bone_pain", "muscle_ache", "fatigue"],
    "urogenital": ["urinary_urgency", "urinary_incontinence", "vaginal_dryness", "dyspareunia"],
    "neurocognitive": ["memory_loss", "poor_concentration", "headache_dizziness"],
    "emotional": ["irritability", "anxiety", "depression", "sleep_disorder"],
    "skin_other": ["dry_skin", "hair_loss"],
}

ALL_SYMPTOMS = [s for symptoms in SYMPTOM_MODULES.values() for s in symptoms]


def generate_trend_curve(days: int, base: float, trend: float, noise: float) -> list[float]:
    """
    生成带趋势和噪声的曲线
    :param base: 基础分值 (1-5)
    :param trend: 整体趋势 (-0.1 ~ 0.1，负数=改善)
    :param noise: 波动幅度 (0.3 ~ 1.0)
    """
    values = []
    for i in range(days):
        # 线性趋势 + 正弦波动（模拟周期性）+ 随机噪声
        trend_component = base + trend * i
        cycle_component = 0.5 * (1 + (i % 7) / 7)  # 周内小幅波动
        noise_component = random.uniform(-noise, noise)
        val = trend_component + cycle_component + noise_component
        values.append(max(0, min(5, round(val))))
    return values


def generate_menstrual_data(days: int) -> list[dict]:
    """
    生成月经数据，模拟一个周期：
    - 前 3 天：正在经期（ongoing）
    - 中间几天：刚结束
    - 后面：无月经
    """
    data = []
    period_start = 2  # 第3天开始经期
    period_length = 5

    for i in range(days):
        if i < period_start:
            data.append({"status": "none", "day": None, "flow": None, "pain": None, "abnormal": None})
        elif i < period_start + period_length:
            day = i - period_start + 1
            flow = max(1, min(5, 5 - day + 1 + random.randint(-1, 1)))  # 逐渐变少
            pain = max(0, min(5, 3 + random.randint(-1, 1)))
            abnormal = random.choice([None, ["血块增多"], ["量比往常多"]]) if random.random() > 0.7 else None
            data.append({
                "status": "ongoing",
                "day": day,
                "flow": flow,
                "pain": pain,
                "abnormal": abnormal,
            })
        else:
            data.append({
                "status": "ended_this_cycle",
                "day": None,
                "flow": None,
                "pain": None,
                "abnormal": None,
            })
    return data


def generate_survey_data(days: int = DAYS) -> list[dict]:
    """生成完整的问卷历史数据"""
    surveys = []
    start_date = datetime.now() - timedelta(days=days)
    menstrual_cycle = generate_menstrual_data(days)
    period_start = 2  # 经期第3天开始，与 generate_menstrual_data 保持一致

    # 定义每个症状的"剧本"：基础值 + 趋势 + 波动
    # 关键：让某些症状呈改善趋势（Demo 亮点）
    symptom_scripts = {
        # 改善中的症状（下降趋势）
        "hot_flash":     {"base": 4.0, "trend": -0.12, "noise": 0.8},   # 潮热从严重→改善
        "night_sweat":   {"base": 3.5, "trend": -0.10, "noise": 0.7},
        "sleep_disorder":{"base": 4.0, "trend": -0.08, "noise": 0.9},   # 睡眠也在好转
        # 稳定偏高的症状
        "irritability":  {"base": 3.0, "trend": -0.02, "noise": 0.8},
        "fatigue":       {"base": 3.0, "trend": -0.03, "noise": 0.7},
        # 轻微症状
        "dry_skin":      {"base": 2.0, "trend": 0.0,   "noise": 0.5},
        "memory_loss":   {"base": 2.0, "trend": 0.01,  "noise": 0.4},
        # 几乎无症状
        "bone_pain":     {"base": 0.5, "trend": 0.0,   "noise": 0.3},
        "hair_loss":     {"base": 1.0, "trend": 0.0,   "noise": 0.3},
    }

    # 为剩余症状补充默认剧本
    for symptom in ALL_SYMPTOMS:
        if symptom not in symptom_scripts:
            symptom_scripts[symptom] = {"base": 1.5, "trend": 0.0, "noise": 0.5}

    # 预计算所有症状的每日分数
    symptom_curves = {
        name: generate_trend_curve(days, **cfg)
        for name, cfg in symptom_scripts.items()
    }

    for i in range(days):
        survey_date = (start_date + timedelta(days=i)).date().isoformat()
        m = menstrual_cycle[i]

        # 构建 symptoms JSON
        symptoms = {name: curve[i] for name, curve in symptom_curves.items()}

        # 整体评分：与症状严重程度负相关，但有主观波动
        avg_symptom = sum(symptoms.values()) / len(symptoms)
        overall = max(1, min(5, int(6 - avg_symptom + random.uniform(-0.5, 0.5))))

        # 备注：在症状剧烈或改善明显时添加
        notes = None
        if i == period_start + 2:
            notes = "经期第二天，潮热特别严重，晚上换了两次衣服"
        elif i == days - 1:
            notes = "最近感觉整体状态好多了，睡眠改善最明显"
        elif symptoms["hot_flash"] > 4 and random.random() > 0.7:
            notes = random.choice([
                "今天开会时突然潮热，很尴尬",
                "半夜盗汗醒来，不太好睡",
            ])

        surveys.append({
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "survey_date": survey_date,
            "menstrual_status": m["status"],
            "menstrual_day": m["day"],
            "menstrual_flow": m["flow"],
            "menstrual_pain": m["pain"],
            "menstrual_abnormal": json.dumps(m["abnormal"], ensure_ascii=False) if m["abnormal"] else None,
            "symptoms": json.dumps(symptoms, ensure_ascii=False),
            "overall_score": overall,
            "notes": notes,
            "created_at": f"{survey_date}T08:30:00",
        })

    return surveys


def export_as_json(surveys: list[dict]) -> None:
    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / "survey_history.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(surveys, f, ensure_ascii=False, indent=2)
    print(f"已生成 {len(surveys)} 条问卷数据 → {path}")


def export_as_sql(surveys: list[dict]) -> None:
    """生成可直接执行的 SQL INSERT 语句"""
    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / "survey_history.sql"

    lines = [
        "-- 模拟问卷数据（21天，覆盖一个经期周期）",
        "DELETE FROM daily_surveys WHERE user_id = 'mock-user-001';",
        "",
    ]
    for s in surveys:
        cols = ["id", "user_id", "survey_date", "menstrual_status", "menstrual_day",
                "menstrual_flow", "menstrual_pain", "menstrual_abnormal",
                "symptoms", "overall_score", "notes", "created_at"]
        vals = [
            f"'{s['id']}'",
            f"'{s['user_id']}'",
            f"'{s['survey_date']}'",
            f"'{s['menstrual_status']}'",
            str(s["menstrual_day"]) if s["menstrual_day"] else "NULL",
            str(s["menstrual_flow"]) if s["menstrual_flow"] else "NULL",
            str(s["menstrual_pain"]) if s["menstrual_pain"] else "NULL",
            f"'{s['menstrual_abnormal']}'" if s["menstrual_abnormal"] else "NULL",
            f"'{s['symptoms']}'",
            str(s["overall_score"]),
            f"'{s['notes']}'" if s["notes"] else "NULL",
            f"'{s['created_at']}'",
        ]
        lines.append(f"INSERT INTO daily_surveys ({', '.join(cols)}) VALUES ({', '.join(vals)});")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"已生成 SQL → {path}")


if __name__ == "__main__":
    surveys = generate_survey_data()
    export_as_json(surveys)
    export_as_sql(surveys)

    # 打印数据摘要
    print(f"\n数据摘要（共 {len(surveys)} 天）：")
    print(f"  日期范围: {surveys[0]['survey_date']} ~ {surveys[-1]['survey_date']}")
    print(f"  经期状态: {surveys[2]['menstrual_status']} (第3天开始)")
    print(f"  首日潮热: {json.loads(surveys[0]['symptoms'])['hot_flash']}分")
    print(f"  末日潮热: {json.loads(surveys[-1]['symptoms'])['hot_flash']}分 (趋势: ↓改善)")
    print(f"  首日整体: {surveys[0]['overall_score']}星")
    print(f"  末日整体: {surveys[-1]['overall_score']}星")
