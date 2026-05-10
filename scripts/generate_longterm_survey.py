"""
生成长期个人症状趋势模拟数据（支持 30天 ~ 365+天）

核心升级：数据模式更符合真实围绝经期女性的经历：
1. 周期性：月经周期规律出现（28±3天周期）
2. 阶段性：不是单调改善，而是"波动中缓慢改善"
3. 季节性：夏季潮热盗汗加重
4. 事件性：某些时间点症状突然加重（压力事件）
"""

import json
import random
import uuid
import math
from datetime import datetime, timedelta
from pathlib import Path

# ============ 配置 ============
USER_ID = "mock-user-001"
DAYS = 90          # 默认 3 个月，Demo 足够展示季度趋势
# DAYS = 365       #  uncomment 生成一年数据
OUTPUT_PATH = Path(__file__).parent.parent / "mock_data"

# 症状定义
SYMPTOMS = [
    "hot_flash", "night_sweat", "palpitations", "chest_tightness",
    "joint_stiffness", "bone_pain", "muscle_ache", "fatigue",
    "urinary_urgency", "urinary_incontinence", "vaginal_dryness", "dyspareunia",
    "memory_loss", "poor_concentration", "headache_dizziness",
    "irritability", "anxiety", "depression", "sleep_disorder",
    "dry_skin", "hair_loss",
]


def generate_menstrual_calendar(days: int, start_date: datetime) -> list[dict]:
    """
    生成规律的月经周期日历。
    围绝经期特征：周期逐渐拉长，经期缩短，量变少。
    """
    cycle_length = 28  # 初始周期28天
    period_length = 5  # 初始经期5天
    last_period_start = -999  # 上次经期开始日索引

    calendar = []
    for i in range(days):
        # 周期逐渐拉长（模拟围绝经期不规律）
        cycle_drift = i // 90  # 每3个月周期变长一点
        current_cycle = cycle_length + cycle_drift * 2 + random.randint(-2, 2)

        # 判断是否在经期
        if i - last_period_start >= current_cycle:
            last_period_start = i
            # 经期长度逐渐缩短
            current_period = max(2, period_length - cycle_drift)
            period_end = i + current_period

        if last_period_start <= i < last_period_start + max(2, period_length - (i // 90) * 1):
            day_in_period = i - last_period_start + 1
            # 血量：前两天多，后几天少
            flow = max(1, 5 - day_in_period + random.randint(-1, 1))
            pain = max(0, min(5, 2 + random.randint(-1, 2)))
            abnormal = random.choice([None, ["血块增多"], ["量比往常少"]]) if random.random() > 0.8 else None
            calendar.append({
                "status": "ongoing",
                "day": day_in_period,
                "flow": flow,
                "pain": pain,
                "abnormal": abnormal,
            })
        elif i == last_period_start + max(2, period_length - (i // 90) * 1):
            # 经期刚结束的那一天
            calendar.append({
                "status": "ended_this_cycle",
                "day": None, "flow": None, "pain": None, "abnormal": None,
            })
        else:
            calendar.append({
                "status": "none",
                "day": None, "flow": None, "pain": None, "abnormal": None,
            })

    return calendar


def symptom_score(day_index: int, total_days: int, symptom_name: str, month_data: dict) -> int:
    """
    计算某一天某个症状的分数（0-5）。
    综合考虑：长期趋势 + 经期影响 + 季节性 + 随机波动 + 压力事件
    """
    progress = day_index / total_days  # 0.0 ~ 1.0

    # ---- 1. 长期趋势（缓慢改善，但有平台期） ----
    if symptom_name in ["hot_flash", "night_sweat", "sleep_disorder"]:
        # 心血管/睡眠：前1/3改善较快，中间平台，后1/3继续缓慢改善
        if progress < 0.33:
            base = 4.5 - 1.5 * (progress / 0.33)  # 4.5 -> 3.0
        elif progress < 0.66:
            base = 3.0 + 0.3 * math.sin(progress * 10)  # 平台期+小幅波动
        else:
            base = 3.0 - 1.0 * ((progress - 0.66) / 0.34)  # 3.0 -> 2.0
    elif symptom_name in ["irritability", "anxiety", "depression"]:
        # 情绪：改善较慢，波动更大
        base = 3.5 - 1.0 * progress + 0.5 * math.sin(progress * 8)
    elif symptom_name in ["fatigue", "joint_stiffness"]:
        # 骨骼肌肉：几乎不变或轻微恶化（围绝经期常见）
        base = 3.0 + 0.3 * progress
    else:
        # 其他症状：轻微波动
        base = 1.5 + 0.5 * math.sin(progress * 6)

    # ---- 2. 经期影响（经期前后症状加重） ----
    cycle_day = day_index % 28
    menstrual_factor = 0
    if 25 <= cycle_day <= 28 or 1 <= cycle_day <= 3:  # 经期前后
        if symptom_name in ["irritability", "fatigue", "headache_dizziness", "chest_tightness"]:
            menstrual_factor = 1.0
        elif symptom_name in ["hot_flash", "sleep_disorder", "anxiety"]:
            menstrual_factor = 0.5

    # ---- 3. 季节性（夏季加重，假设数据从春季开始） ----
    # day_index 0 = 春季，~90天后是夏季
    season = (day_index % 365) / 365  # 年内位置
    summer_peak = math.exp(-((season - 0.33) ** 2) / 0.02)  # 夏季高峰（高斯分布）
    seasonal_factor = 0
    if symptom_name in ["hot_flash", "night_sweat", "dry_skin"]:
        seasonal_factor = 1.0 * summer_peak

    # ---- 4. 压力事件（随机 spikes） ----
    stress_factor = 0
    if day_index in month_data.get("stress_days", []):
        if symptom_name in ["sleep_disorder", "irritability", "anxiety", "headache_dizziness"]:
            stress_factor = 1.5

    # ---- 5. 随机噪声 ----
    noise = random.uniform(-0.6, 0.6)

    # 综合计算
    score = base + menstrual_factor + seasonal_factor + stress_factor + noise
    return max(0, min(5, round(score)))


def generate_longterm_data(days: int = DAYS) -> list[dict]:
    """生成长期问卷历史数据"""
    surveys = []
    start_date = datetime.now() - timedelta(days=days)
    menstrual = generate_menstrual_calendar(days, start_date)

    # 随机生成几个"压力事件日"（症状 spike）
    stress_days = random.sample(range(days // 4, days), k=min(3, days // 30))
    month_data = {"stress_days": stress_days}

    # 记录每个月的摘要（用于后续分析）
    monthly_summary = {}

    for i in range(days):
        survey_date = (start_date + timedelta(days=i)).date()
        m = menstrual[i]

        # 生成当天所有症状分数
        symptoms = {name: symptom_score(i, days, name, month_data) for name in SYMPTOMS}

        # 整体评分：与症状严重程度负相关
        avg = sum(symptoms.values()) / len(symptoms)
        overall = max(1, min(5, int(6 - avg + random.uniform(-0.4, 0.4))))

        # 备注：只在关键日子生成
        notes = None
        if i in stress_days:
            notes = random.choice([
                "最近工作压力大，症状好像加重了一些",
                "家里有点事，这几天睡得不太好",
                "出差换了环境，潮热又频繁了",
            ])
        elif m["status"] == "ongoing" and m["day"] == 1 and random.random() > 0.7:
            notes = "经期第一天，症状比较明显"
        elif i == days - 1:
            # 最后一天生成总结性备注
            hot_flash_first = symptom_score(0, days, "hot_flash", month_data)
            hot_flash_last = symptoms["hot_flash"]
            if hot_flash_first > hot_flash_last:
                notes = f"坚持记录{days}天了，潮热从{hot_flash_first}分降到了{hot_flash_last}分，继续加油"
            else:
                notes = f"已经记录{days}天了，虽然过程有起伏，但整体在慢慢适应"

        surveys.append({
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "survey_date": survey_date.isoformat(),
            "menstrual_status": m["status"],
            "menstrual_day": m["day"],
            "menstrual_flow": m["flow"],
            "menstrual_pain": m["pain"],
            "menstrual_abnormal": json.dumps(m["abnormal"], ensure_ascii=False) if m["abnormal"] else None,
            "symptoms": json.dumps(symptoms, ensure_ascii=False),
            "overall_score": overall,
            "notes": notes,
            "created_at": f"{survey_date.isoformat()}T08:30:00",
        })

        # 按月统计（用于报告页的月度对比）
        month_key = survey_date.strftime("%Y-%m")
        if month_key not in monthly_summary:
            monthly_summary[month_key] = {"symptoms": [], "overall": []}
        monthly_summary[month_key]["symptoms"].append(avg)
        monthly_summary[month_key]["overall"].append(overall)

    # 打印月度摘要
    print("\n月度症状均值摘要：")
    for month, data in sorted(monthly_summary.items()):
        avg_symptom = sum(data["symptoms"]) / len(data["symptoms"])
        avg_overall = sum(data["overall"]) / len(data["overall"])
        print(f"  {month}: 症状均分 {avg_symptom:.1f} | 整体评分 {avg_overall:.1f}")

    return surveys


def export(surveys: list[dict]) -> None:
    OUTPUT_PATH.mkdir(exist_ok=True)

    # JSON
    json_path = OUTPUT_PATH / f"survey_history_{len(surveys)}d.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(surveys, f, ensure_ascii=False, indent=2)
    print(f"\n已生成 {len(surveys)} 条问卷数据 → {json_path}")

    # SQL
    sql_path = OUTPUT_PATH / f"survey_history_{len(surveys)}d.sql"
    lines = [f"-- 模拟问卷数据（{len(surveys)}天）", f"DELETE FROM daily_surveys WHERE user_id = '{USER_ID}';", ""]
    for s in surveys:
        cols = ["id", "user_id", "survey_date", "menstrual_status", "menstrual_day",
                "menstrual_flow", "menstrual_pain", "menstrual_abnormal",
                "symptoms", "overall_score", "notes", "created_at"]
        vals = [
            f"'{s['id']}'", f"'{s['user_id']}'", f"'{s['survey_date']}'", f"'{s['menstrual_status']}'",
            str(s["menstrual_day"]) if s["menstrual_day"] else "NULL",
            str(s["menstrual_flow"]) if s["menstrual_flow"] else "NULL",
            str(s["menstrual_pain"]) if s["menstrual_pain"] else "NULL",
            f"'{s['menstrual_abnormal']}'" if s["menstrual_abnormal"] else "NULL",
            f"'{s['symptoms']}'", str(s["overall_score"]),
            f"'{s['notes']}'" if s["notes"] else "NULL",
            f"'{s['created_at']}'",
        ]
        lines.append(f"INSERT INTO daily_surveys ({', '.join(cols)}) VALUES ({', '.join(vals)});")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"已生成 SQL → {sql_path}")

    # 数据摘要
    first = surveys[0]
    last = surveys[-1]
    first_sym = json.loads(first["symptoms"])
    last_sym = json.loads(last["symptoms"])
    print(f"\n数据摘要（共 {len(surveys)} 天）：")
    print(f"  日期范围: {first['survey_date']} ~ {last['survey_date']}")
    print(f"  潮热: {first_sym['hot_flash']}分 → {last_sym['hot_flash']}分")
    print(f"  睡眠: {first_sym['sleep_disorder']}分 → {last_sym['sleep_disorder']}分")
    print(f"  情绪: {first_sym['irritability']}分 → {last_sym['irritability']}分")
    print(f"  整体: {first['overall_score']}星 → {last['overall_score']}星")
    print(f"  经期周期数: 约 {len(surveys) // 28} 个")


if __name__ == "__main__":
    # 修改这里切换数据量
    # DAYS = 30   # 1个月
    # DAYS = 90   # 3个月（默认，Demo推荐）
    # DAYS = 180  # 半年
    # DAYS = 365  # 1年

    surveys = generate_longterm_data(DAYS)
    export(surveys)
