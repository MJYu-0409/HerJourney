"""
基于新症状标签体系的增强版 Mock 数据生成脚本

改进点：
1. 15个核心症状，按4大维度精简组织
2. 睡眠障碍拆分为3个独立维度（入睡困难/夜间易醒/早醒）
3. 整体评分方向反转：1=很好，5=很差
4. 增加用药/干预记录
5. 经期字段精简（末次月经距今天数、经量三档、经血异常三档）
6. 增加每周长期健康补充项
7. 保留症状相关性约束、极端测试日、断签模拟
"""

import json
import random
import sys
import uuid
import math
import re
from datetime import datetime, timedelta
from pathlib import Path

# 修复 Windows 终端 UTF-8 输出
sys.stdout.reconfigure(encoding="utf-8")

# ============ 全局配置 ============
SEED = 42
random.seed(SEED)

USER_ID = "mock-user-001"
NICKNAME = "李女士"
MENOPAUSE_STAGE = "围绝经期"
DAYS = 90
ATTENDANCE_RATE = 0.75
OUTPUT_PATH = Path(__file__).parent.parent / "mock_data"

# ============ 症状标签库（15个核心症状，4大维度） ============

SYMPTOMS = [
    # 1. 血管舒缩症状（3个）
    "hot_flash",          # 潮热（白天突然燥热、面颈发红）
    "night_sweat",        # 夜间盗汗（入睡后出汗、惊醒）
    "palpitations",       # 心慌心悸（无诱因心跳加快、心慌）

    # 2. 精神情绪症状（4个）
    "irritability",       # 烦躁易怒（易生气、情绪波动大）
    "anxiety",            # 焦虑紧张（莫名担忧、坐立不安）
    "depression",         # 情绪低落（提不起劲、低落压抑）
    "poor_concentration", # 注意力涣散（专注力下降、记性差）

    # 3. 睡眠障碍症状（3个）
    "sleep_onset_difficulty",  # 入睡困难（超过30分钟睡不着）
    "nighttime_awakening",     # 夜间易醒（频繁醒来、醒后难眠）
    "early_awakening",         # 早醒（比平时早醒2小时以上）

    # 4. 泌尿生殖 & 骨骼躯体症状（5个）
    "vaginal_dryness",    # 阴道干涩（同房不适、干涩疼痛）
    "urinary_urgency",    # 尿频尿急（频繁想上厕所）
    "recurrent_uti",      # 反复尿路感染（尿道刺痛、炎症）
    "joint_muscle_pain",  # 关节骨骼酸痛（肩颈腰、膝盖僵硬疼）
    "fatigue",            # 乏力疲惫（全天无精神、易累）
]

# 症状相关性组（同组内症状当日分数差异不超过 ±1）
CORRELATION_GROUPS = {
    "vasomotor": ["hot_flash", "night_sweat", "palpitations"],
    "emotional": ["irritability", "anxiety", "depression"],
    "sleep": ["sleep_onset_difficulty", "nighttime_awakening", "early_awakening"],
    "neurocognitive": ["poor_concentration"],
    "urogenital": ["vaginal_dryness", "urinary_urgency", "recurrent_uti"],
    "musculoskeletal": ["joint_muscle_pain", "fatigue"],
}

# 用药/干预选项
MEDICATION_OPTIONS = ["无", "中药调理", "激素治疗", "钙片维生素", "助眠药物", "其他"]

# 极端测试日配置（day_index -> 所有症状分数）
EXTREME_DAYS = {
    20: 0,   # 全0日：完全无症状
    45: 5,   # 全5日：全面崩溃
    70: 1,   # 全1日：轻微症状日
}


# ============ 1. 经期数据生成 ============

def generate_menstrual_calendar(days: int) -> list[dict]:
    """生成规律月经周期，围绝经期周期逐渐拉长"""
    cycle_base = 28
    period_len = 5
    last_start = -999
    calendar = []

    for i in range(days):
        cycle_drift = i // 90
        current_cycle = cycle_base + cycle_drift * 2 + random.randint(-2, 2)

        if i - last_start >= current_cycle:
            last_start = i

        period_current = max(2, period_len - cycle_drift)

        if last_start <= i < last_start + period_current:
            # 正在经期
            day_in = i - last_start + 1
            day_display = min(day_in, 7)  # 超过7天统一标记为7
            flow = random.choice(["少", "中", "多"])
            pain = max(1, min(5, 2 + random.randint(-1, 2)))
            abnormal = random.choice(["无", "淋漓不尽", "非经期出血"]) if random.random() > 0.85 else "无"
            calendar.append({
                "status": "ongoing",
                "days_since_last_period": day_in,
                "day": day_display,
                "flow": flow,
                "pain": pain,
                "abnormal": abnormal,
            })
        elif i == last_start + period_current:
            # 经期刚结束
            days_since = period_current + 1
            calendar.append({
                "status": "ended_this_cycle",
                "days_since_last_period": days_since,
                "day": None,
                "flow": None,
                "pain": None,
                "abnormal": None,
            })
        else:
            # 非经期
            days_since = i - last_start + 1
            calendar.append({
                "status": "none",
                "days_since_last_period": days_since,
                "day": None,
                "flow": None,
                "pain": None,
                "abnormal": None,
            })

    return calendar


# ============ 2. 症状数据生成 ============

def generate_daily_symptoms(day_index: int, total_days: int, extreme_value: int | None) -> dict[str, int]:
    """生成某天所有症状分数，带相关性约束"""
    if extreme_value is not None:
        return {s: extreme_value for s in SYMPTOMS}

    progress = day_index / total_days
    symptoms = {}

    # 为每个相关性组生成组内基础因子
    group_factors = {}
    for group_name, members in CORRELATION_GROUPS.items():
        trend = math.sin(progress * math.pi * 2) * 0.3
        seasonal = 0.5 if 60 <= day_index % 365 <= 150 else 0
        noise = random.uniform(-0.8, 0.8)
        group_factors[group_name] = trend + seasonal + noise

    # 按组分配症状分数
    assigned = set()
    for group_name, members in CORRELATION_GROUPS.items():
        base = group_factors[group_name]
        anchor_score = max(0, min(5, round(2.5 + base * 2.5)))
        for symptom in members:
            if symptom in assigned:
                continue
            deviation = random.randint(-1, 1)
            symptoms[symptom] = max(0, min(5, anchor_score + deviation))
            assigned.add(symptom)

    return symptoms


# ============ 3. 每周长期健康补充项 ============

def generate_weekly_supplement(day_index: int) -> dict | None:
    """每周生成一次长期健康补充项（每周第0天生成）"""
    if day_index % 7 != 0:
        return None

    return {
        "weight_change": random.choice(["增加", "减少", "无变化"]),
        "blood_pressure": random.choice(["正常", "偏高", "偏低"]),
        "persistent_joint_pain": random.choice([True, False]),
        "sexual_discomfort": random.choice([True, False]),
    }


# ============ 4. 问卷数据生成 ============

def generate_survey_data(days: int = DAYS, attendance: float = ATTENDANCE_RATE) -> list[dict]:
    """生成问卷历史数据，支持断签"""
    surveys = []
    start_date = datetime.now() - timedelta(days=days)
    menstrual = generate_menstrual_calendar(days)

    attendance_days = sorted(random.sample(range(days), k=int(days * attendance)))

    for i in attendance_days:
        survey_date = (start_date + timedelta(days=i)).date()
        m = menstrual[i]
        extreme = EXTREME_DAYS.get(i)

        symptoms = generate_daily_symptoms(i, days, extreme)

        # 整体评分：1=很好，5=很差（与症状严重程度正相关）
        avg = sum(symptoms.values()) / len(symptoms)
        overall = max(1, min(5, round(1 + avg * 0.8 + random.uniform(-0.3, 0.3))))

        # 用药记录：症状严重时更可能用药
        if avg >= 3.5:
            medication = random.choice(["中药调理", "激素治疗", "助眠药物", "其他"])
        elif avg >= 2:
            medication = random.choice(["无", "钙片维生素", "中药调理"])
        else:
            medication = "无"

        # 每周补充项
        weekly = generate_weekly_supplement(i)

        # 备注
        notes = None
        if extreme == 0:
            notes = "今天状态特别好，一个症状都没有，难得！"
        elif extreme == 5:
            notes = "今天全面崩溃，所有症状一起来了，想哭"
        elif extreme == 1:
            notes = "今天整体还行，只有轻微不适"
        elif m["status"] == "ongoing" and m["day"] == 1 and random.random() > 0.7:
            notes = "经期第一天，各种症状都冒出来了"
        elif i == attendance_days[-1]:
            notes = f"坚持记录{i+1}天了，虽然起伏不断，但已经成习惯"

        surveys.append({
            "id": str(uuid.UUID(int=random.getrandbits(128))),
            "user_id": USER_ID,
            "survey_date": survey_date.isoformat(),
            "menstrual_status": m["status"],
            "days_since_last_period": m["days_since_last_period"],
            "menstrual_day": m["day"],
            "menstrual_flow": m["flow"],
            "menstrual_pain": m["pain"],
            "menstrual_abnormal": m["abnormal"],
            "symptoms": json.dumps(symptoms, ensure_ascii=False),
            "overall_score": overall,
            "medication": medication,
            "weekly_supplement": json.dumps(weekly, ensure_ascii=False) if weekly else None,
            "notes": notes,
            "created_at": f"{survey_date.isoformat()}T08:30:00",
        })

    return surveys


# ============ 5. AI 问答记录生成 ============

def generate_chat_history() -> list[dict]:
    """生成 AI 问答记录（AI生成经验帖的输入素材）"""
    session_id = str(uuid.UUID(int=random.getrandbits(128)))
    now = datetime.now()

    conversations = [
        ("user", "最近老是潮热，尤其是在开会的时候，特别尴尬，有什么办法缓解吗？"),
        ("assistant", "【情绪共情】完全理解你的感受，在公共场合突然潮热确实很让人不自在，很多姐妹都有类似的经历。\n\n【科普解释】潮热是更年期最常见的症状之一，主要是因为体内雌激素水平波动，影响了体温调节中枢。\n\n【应对建议】\n1. 穿分层衣服：内搭选棉质透气面料，外面加一件薄开衫，热的时候能快速脱掉\n2. 随身携带小风扇或冰凉贴，感觉热的时候及时降温\n3. 避免辛辣食物、咖啡和酒精，这些会刺激血管扩张\n\n【温暖结尾】慢慢来，找到适合自己的方法，潮热是可以管理的。\n\n*本回答参考更年期医学文献，仅供健康参考"),
        ("user", "那盗汗呢？我晚上经常出一身汗，枕头都湿透了"),
        ("assistant", "【情绪共情】盗汗确实特别影响睡眠质量，半夜被汗湿醒的感觉真的很糟糕。\n\n【科普解释】盗汗和潮热是'姐妹症状'，都是血管舒缩功能不稳定的表现。夜间体温调节中枢敏感度增加，更容易出现大量出汗。\n\n【应对建议】\n1. 睡前2小时不要剧烈运动或吃辛辣食物\n2. 卧室温度调低一些，选择透气性好的纯棉床品\n3. 床边放一套备用睡衣和毛巾，万一汗湿了可以快速更换\n\n【温暖结尾】坚持记录症状变化，你会发现哪些方法对自己最有效。晚安，好梦～\n\n*本回答参考更年期医学文献，仅供健康参考"),
        ("user", "睡眠也很差，经常半夜醒来就再也睡不着了"),
        ("assistant", "【情绪共情】失眠的日子真的很难受，第二天还要强打精神工作，特别辛苦。\n\n【科普解释】更年期失眠和雌激素下降有关，雌激素本身有促进睡眠的作用。另外，潮热盗汗也会打断睡眠周期。\n\n【应对建议】\n1. 建立固定作息：每天同一时间上床和起床，周末也不例外\n2. 午睡控制在20分钟以内，下午3点后不再睡\n3. 睡前泡脚15分钟，用40度左右的水，有助于身体放松\n\n【温暖结尾】睡眠改善需要时间，别给自己太大压力。你已经做得很好了。\n\n*本回答参考更年期医学文献，仅供健康参考"),
        ("user", "我有点焦虑，总是担心各种事情，这是更年期引起的吗？"),
        ("assistant", "【情绪共情】焦虑的感觉真的很消耗人，总是脑子里转个不停，停不下来。你的感受是真实的。\n\n【科普解释】更年期焦虑确实和激素变化有关。雌激素参与调节大脑中的血清素水平，雌激素下降会影响情绪稳定性。\n\n【应对建议】\n1. 每天留出10分钟做深呼吸或冥想，帮助神经系统放松\n2. 适度运动，比如快走30分钟，可以促进内啡肽分泌\n3. 如果焦虑严重影响生活，建议咨询心理医生或妇科医生\n\n【温暖结尾】焦虑不是你的错，是身体在调整。照顾好自己，一步一步来。\n\n*本回答参考更年期医学文献，仅供健康参考"),
        ("user", "这些情况一般要持续多久啊？"),
        ("assistant", "【情绪共情】想知道尽头在哪里，这种心情我特别理解。面对不确定，人会本能地想要一个期限。\n\n【科普解释】围绝经期通常持续2-8年，但症状的严重程度和持续时间因人而异。大部分女性的潮热盗汗在绝经后2-3年内明显减轻。\n\n【应对建议】\n1. 把注意力放在'今天能做什么让自己舒服一点'，而不是'还要多久'\n2. 每天坚持记录症状，你会发现自己的规律和进步\n3. 和医生保持沟通，必要时可以考虑激素替代疗法等医学干预\n\n【温暖结尾】无论持续多久，你都不是一个人在经历。我们会一直陪着你。\n\n*本回答参考更年期医学文献，仅供健康参考"),
    ]

    messages = []
    for i, (role, content) in enumerate(conversations):
        messages.append({
            "id": str(uuid.UUID(int=random.getrandbits(128))),
            "user_id": USER_ID,
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": (now - timedelta(hours=len(conversations) - i)).isoformat(),
        })

    return messages


# ============ 6. 社区帖子生成（50条） ============

POST_AUTHORS = [
    {"nickname": "静姐_48", "stage": "围绝经期"},
    {"nickname": "小花的妈妈", "stage": "围绝经期"},
    {"nickname": "李女士", "stage": "围绝经期"},
    {"nickname": "健康快乐", "stage": "绝经后"},
    {"nickname": "夜半听雨", "stage": "围绝经期"},
    {"nickname": "阳光大姐", "stage": "围绝经期"},
    {"nickname": "优雅老去", "stage": "绝经后"},
]

# 症状关键词池（确保搜索每个关键词都有结果）
# 新标签体系下的中文症状 → 英文字段名映射
SYMPTOM_KEYWORDS = {
    "潮热": ["hot_flash"],
    "盗汗": ["night_sweat"],
    "心慌": ["palpitations"],
    "烦躁": ["irritability"],
    "焦虑": ["anxiety"],
    "情绪低落": ["depression"],
    "注意力不集中": ["poor_concentration"],
    "失眠": ["sleep_onset_difficulty", "nighttime_awakening", "early_awakening"],
    "入睡困难": ["sleep_onset_difficulty"],
    "早醒": ["early_awakening"],
    "阴道干涩": ["vaginal_dryness"],
    "尿频": ["urinary_urgency"],
    "尿路感染": ["recurrent_uti"],
    "关节痛": ["joint_muscle_pain"],
    "乏力": ["fatigue"],
}

POST_TEMPLATES = [
    # 经验帖模板
    {"type": "experience", "title": "{keyword}三个月后，我终于找到了缓解方法", "content": "从去年开始，{keyword}突然严重起来。最严重的时候，{detail}。\n\n我试过好几种方法，最后发现这几招对我最有效：\n\n1. {tip1}\n2. {tip2}\n3. {tip3}\n\n现在三个月过去了，虽然还会{keyword_short}，但频率和强度都明显降低了。姐妹们不要慌，这是一个可以管理的过程。", "keywords": ["潮热", "盗汗", "失眠", "焦虑", "关节痛", "乏力"]},
    {"type": "experience", "title": "{keyword}的日子，我是怎么熬过来的", "content": "更年期{keyword}真的太折磨人了。以前{contrast}，现在{now_state}。\n\n分享一下我的修复计划：\n\n- {tip1}\n- {tip2}\n- {tip3}\n- {tip4}\n\n最重要的，是接受\"现在不如以前\"这个事实。不焦虑，反而更容易改善。", "keywords": ["失眠", "焦虑", "烦躁", "乏力", "情绪低落"]},
    {"type": "experience", "title": "给刚进入更年期的姐妹：{keyword}都是正常的", "content": "48岁那年，我第一次出现{keyword}的时候，以为自己得了什么大病。跑了好几次医院，检查结果都是\"正常\"。\n\n后来我才慢慢了解，这些都是更年期的正常表现。知道这是正常的，心理压力就小了很多。现在我用小程序每天记录症状，看着数据慢慢变化，心里有底多了。", "keywords": ["潮热", "盗汗", "失眠", "注意力不集中", "心慌"]},
    # 求助帖模板
    {"type": "general", "title": "{keyword}越来越严重，姐妹们有什么办法？", "content": "最近{keyword}越来越频繁了，{detail}。试过{tip1}但效果不明显。\n\n有没有姐妹有类似经历？求分享有效的方法，谢谢！", "keywords": ["潮热", "失眠", "关节痛", "阴道干涩", "尿频", "尿路感染"]},
    {"type": "general", "title": "因为{keyword}，今天去医院做了{check}检查", "content": "最近{keyword}一直不见好转，医生建议围绝经期女性每年做一次{check}，今天去做了，结果{result}。医生说要多{advice}。姐妹们有定期检查吗？", "keywords": ["潮热", "乏力", "关节痛"]},
    # 报告帖模板
    {"type": "report", "title": "我的30天症状报告：{keyword}改善明显", "content": "连续打卡30天后，生成了我的第一份症状报告。\n\n数据显示：\n- {keyword}：从平均{score1}分降到{score2}分 ⬇️\n- 盗汗：从{score3}分降到{score4}分 ⬇️\n- 睡眠：从{score5}分降到{score6}分 ⬇️\n\nAI 解读说我的心血管相关症状呈现明显下降趋势，建议继续保持当前的作息和运动习惯。\n\n把这份报告分享到社区，希望能给有类似症状的姐妹一些参考。", "keywords": ["潮热", "失眠", "焦虑", "烦躁"]},
]

# 模板填充内容库
FILL_CONTENT = {
    "detail": {
        "潮热": "一天要换两三件衣服，晚上更是睡不安稳",
        "盗汗": "半夜被汗湿醒，枕头都湿透了",
        "失眠": "半夜两三点眼睛还睁得大大的",
        "入睡困难": "躺下后翻来覆去一个多小时还睡不着",
        "早醒": "凌晨四五点就醒了，再也睡不着",
        "焦虑": "脑子里转个不停，停不下来",
        "烦躁": "一点小事就发脾气，事后又后悔",
        "情绪低落": "整天提不起劲，什么都不想做",
        "关节痛": "早上起床关节僵硬，活动好久才缓解",
        "阴道干涩": "很不舒服，影响了日常生活",
        "尿频": "晚上要起夜三四次，严重影响睡眠",
        "尿路感染": "上厕所的时候刺痛，特别难受",
        "乏力": "整天没精神，什么事都不想做",
        "心慌": "莫名其妙心跳加速，有点害怕",
        "注意力不集中": "工作老是走神，效率特别低",
    },
    "tip1": {
        "潮热": "穿分层衣服：棉质打底+薄外套，热的时候能快速脱掉",
        "盗汗": "睡前泡脚：用40度左右的温水泡15分钟",
        "失眠": "固定作息：不管几点睡着，早上七点准时起床",
        "入睡困难": "睡前1小时不看手机，调暗卧室灯光",
        "早醒": "晚上少喝水，避免凌晨被尿意唤醒",
        "焦虑": "每天留出10分钟做深呼吸或冥想",
        "烦躁": "感觉要发火前先深呼吸10次",
        "情绪低落": "每天晒15分钟太阳，促进血清素分泌",
        "关节痛": "每天做温和的拉伸运动，不要久坐",
        "阴道干涩": "使用保湿产品，必要时咨询医生",
        "尿频": "下午3点后控制饮水量",
        "尿路感染": "多喝水、不憋尿，必要时就医检查",
        "乏力": "适度运动，比如快走30分钟",
        "心慌": "感觉心慌时坐下休息，做深呼吸",
        "注意力不集中": "把大任务拆成小步骤，一次只做一件事",
    },
    "tip2": {
        "潮热": "随身携带小风扇或冰凉贴，感觉热的时候及时降温",
        "盗汗": "卧室温度调低一些，选择透气性好的纯棉床品",
        "失眠": "午睡控制在20分钟以内，下午3点后不再睡",
        "入睡困难": "尝试白噪音或冥想音频帮助入眠",
        "早醒": "白天增加户外活动时间，调节生物钟",
        "焦虑": "适度运动，快走30分钟可以促进内啡肽分泌",
        "烦躁": "找闺蜜聊聊天，把情绪说出来",
        "情绪低落": "写情绪日记，把负面想法写下来",
        "关节痛": "补充钙和维生素D",
        "阴道干涩": "多喝水，保持身体水分",
        "尿频": "避免咖啡因和酒精摄入",
        "尿路感染": "注意私处卫生，穿棉质内裤",
        "乏力": "饮食均衡，多吃蛋白质和蔬果",
        "心慌": "避免浓茶、咖啡和酒精",
        "注意力不集中": "工作间隙做5分钟眼保健操",
    },
    "tip3": {
        "潮热": "避免辛辣食物、咖啡和酒精",
        "盗汗": "床边放一套备用睡衣和毛巾",
        "失眠": "睡前泡脚15分钟，有助于身体放松",
        "入睡困难": "不要在床上玩手机，建立床=睡觉的条件反射",
        "早醒": "醒后不要看时间，闭眼尝试继续入睡",
        "焦虑": "如果严重影响生活，建议咨询心理医生",
        "烦躁": "每天写感恩日记，把注意力放在美好的事上",
        "情绪低落": "培养一个小爱好，转移注意力",
        "关节痛": "必要时可以使用热敷缓解",
        "阴道干涩": "选择棉质内裤，避免紧身裤",
        "尿频": "练习凯格尔运动，增强盆底肌",
        "尿路感染": "如反复感染，建议做泌尿系统检查",
        "乏力": "不要过度勉强自己，该休息就休息",
        "心慌": "如频繁发作建议做心电图检查",
        "注意力不集中": "保证充足睡眠，这是专注力恢复的基础",
    },
    "tip4": {
        "失眠": "卧室改造：换了遮光窗帘，买了白噪音机",
        "入睡困难": "睡前喝一杯温热的洋甘菊茶",
        "早醒": "尝试渐进式肌肉放松法",
        "焦虑": "和医生保持沟通，必要时考虑医学干预",
        "烦躁": "接受\"现在情绪不如以前稳定\"这个事实",
        "情绪低落": "每周约朋友聚一次，社交对抗孤独感",
        "乏力": "每天做一件让自己开心的小事",
        "关节痛": "游泳是最好的低冲击运动",
        "心慌": "随身携带记录本，记录发作时间和诱因",
    },
    "contrast": {
        "失眠": "躺下就能睡着",
        "入睡困难": "秒睡星人",
        "早醒": "一觉睡到天亮",
        "焦虑": "心态很平和",
        "烦躁": "脾气很好",
        "情绪低落": "每天都挺开心",
        "乏力": "精力充沛",
    },
    "now_state": {
        "失眠": "半夜两三点眼睛还睁得大大的",
        "入睡困难": "翻来覆去睡不着",
        "早醒": "凌晨四五点就醒了",
        "焦虑": "总是担心各种事情",
        "烦躁": "一点小事就想发火",
        "情绪低落": "整天提不起劲",
        "乏力": "整天没精神",
    },
    "keyword_short": {
        "潮热": "潮热",
        "盗汗": "盗汗",
        "失眠": "失眠",
        "入睡困难": "睡不着",
        "早醒": "早醒",
        "焦虑": "焦虑",
        "烦躁": "烦躁",
        "情绪低落": "情绪低落",
        "关节痛": "关节痛",
        "阴道干涩": "不舒服",
        "尿频": "尿频",
        "尿路感染": "尿路感染",
        "乏力": "乏力",
        "心慌": "心慌",
        "注意力不集中": "注意力不集中",
    },
    "check": {
        "潮热": "骨密度",
        "乏力": "骨密度",
        "关节痛": "骨密度和激素水平",
    },
    "result": {
        "潮热": "正常",
        "乏力": "轻微骨质疏松，需要补钙",
        "关节痛": "骨密度正常，但维生素D偏低",
    },
    "advice": {
        "潮热": "补钙、多晒太阳、适当运动",
        "乏力": "补充钙和维生素D，适度负重运动",
        "关节痛": "补充维生素D，加强关节周围肌肉锻炼",
    },
}


def generate_posts(count: int = 50) -> list[dict]:
    """生成社区帖子，确保每个症状关键词至少出现2次"""
    posts = []
    now = datetime.now()
    keyword_coverage = {k: 0 for k in SYMPTOM_KEYWORDS}

    # 第一轮：确保每个关键词至少被覆盖2次
    for keyword in SYMPTOM_KEYWORDS:
        for _ in range(2):
            matching = [t for t in POST_TEMPLATES if keyword in t["keywords"]]
            tmpl = random.choice(matching) if matching else random.choice(POST_TEMPLATES)
            posts.append(_create_post(tmpl, keyword, now))
            keyword_coverage[keyword] += 1

    # 第二轮：随机填充到目标数量
    remaining = count - len(posts)
    for _ in range(remaining):
        tmpl = random.choice(POST_TEMPLATES)
        keyword = random.choice(tmpl["keywords"])
        posts.append(_create_post(tmpl, keyword, now))
        keyword_coverage[keyword] += 1

    # 打乱顺序，按时间倒序排列
    random.shuffle(posts)
    for i, p in enumerate(posts):
        offset = timedelta(minutes=random.randint(i * 30, (i + 1) * 60))
        p["created_at"] = (now - offset).isoformat()
        p["published_at"] = p["created_at"]

    posts.sort(key=lambda x: x["created_at"], reverse=True)
    return posts


def _create_post(tmpl: dict, keyword: str, base_time: datetime) -> dict:
    """根据模板创建单条帖子"""
    author = random.choice(POST_AUTHORS)
    is_official = author["nickname"] == "她伴官方"

    # 填充模板
    title = tmpl["title"]
    content = tmpl["content"]
    for placeholder in ["keyword", "detail", "tip1", "tip2", "tip3", "tip4", "contrast", "now_state", "keyword_short", "check", "result", "advice", "score1", "score2", "score3", "score4", "score5", "score6"]:
        marker = f"{{{placeholder}}}"
        if marker in title:
            value = keyword if placeholder == "keyword" else FILL_CONTENT.get(placeholder, {}).get(keyword, "")
            if not value and placeholder.startswith("score"):
                value = str(random.randint(2, 5))
            title = title.replace(marker, value)
        if marker in content:
            value = keyword if placeholder == "keyword" else FILL_CONTENT.get(placeholder, {}).get(keyword, "")
            if not value and placeholder.startswith("score"):
                value = str(random.randint(2, 5))
            content = content.replace(marker, value)

    # 清理未填充的占位符
    title = re.sub(r"\{[^}]+\}", "", title)
    content = re.sub(r"\{[^}]+\}", "", content)

    views = random.randint(50, 3000) if not is_official else random.randint(1500, 6000)
    likes = int(views * random.uniform(0.05, 0.2))
    comments = int(views * random.uniform(0.02, 0.1))

    tags = [f"#{keyword}", f"#{'围绝经期' if author['stage'] == '围绝经期' else '绝经后'}"]
    if tmpl["type"] == "experience":
        tags.append("#经验分享")
    elif tmpl["type"] == "report":
        tags.append("#症状报告")
    elif tmpl["type"] == "general":
        tags.append("#求助")

    return {
        "id": str(uuid.UUID(int=random.getrandbits(128))),
        "user_id": None if is_official else f"user-{random.randint(1000, 9999)}",
        "post_type": "official" if is_official else tmpl["type"],
        "title": title,
        "content": content,
        "images": None,
        "voice_url": None,
        "tags": json.dumps(tags, ensure_ascii=False),
        "is_ai_generated": False,
        "status": "published",
        "likes": likes,
        "views": views,
        "created_at": base_time.isoformat(),
        "published_at": base_time.isoformat(),
    }


# ============ 导出 ============

def export_json(data: list[dict], filename: str) -> None:
    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  JSON → {path} ({len(data)} 条)")


def export_sql(table: str, data: list[dict], filename: str) -> None:
    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / filename

    if not data:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"-- {table} 无数据\n")
        return

    keys = list(data[0].keys())
    lines = [f"-- {table} Mock 数据 ({len(data)} 条)", f"DELETE FROM {table} WHERE user_id = '{USER_ID}';", ""]

    for row in data:
        vals = []
        for k in keys:
            v = row[k]
            if v is None:
                vals.append("NULL")
            elif isinstance(v, bool):
                vals.append("true" if v else "false")
            elif isinstance(v, int) or isinstance(v, float):
                vals.append(str(v))
            else:
                vals.append("'" + str(v).replace("'", "''") + "'")
        lines.append(f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({', '.join(vals)});")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  SQL  → {path}")


# ============ 主程序 ============

if __name__ == "__main__":
    print("=" * 50)
    print("新标签体系 Mock 数据生成")
    print(f"配置: {DAYS}天 | 打卡率{ATTENDANCE_RATE*100:.0f}% | 种子{SEED}")
    print("=" * 50)

    # 1. 问卷数据
    print("\n[1/3] 生成问卷数据...")
    surveys = generate_survey_data()
    print(f"  实际打卡天数: {len(surveys)} / {DAYS} (断签 {DAYS - len(surveys)} 天)")

    extreme_count = sum(1 for s in surveys if json.loads(s["symptoms"]).get("hot_flash") in [0, 5] and len(set(json.loads(s["symptoms"]).values())) == 1)
    print(f"  极端测试日: {extreme_count} 天")

    symptoms_first = json.loads(surveys[0]["symptoms"])
    vasomotor = [symptoms_first.get(s) for s in CORRELATION_GROUPS["vasomotor"]]
    print(f"  血管舒缩组首日: {vasomotor} (差异≤1: {'✓' if max(vasomotor)-min(vasomotor) <= 1 else '✗'})")

    # 统计每周补充项
    weekly_count = sum(1 for s in surveys if s["weekly_supplement"] is not None)
    print(f"  每周补充项记录: {weekly_count} 条")

    export_json(surveys, f"survey_enhanced_{DAYS}d.json")
    export_sql("daily_surveys", surveys, f"survey_enhanced_{DAYS}d.sql")

    # 2. 聊天数据
    print("\n[2/3] 生成 AI 问答记录...")
    chats = generate_chat_history()
    export_json(chats, "chat_history.json")
    export_sql("chat_messages", chats, "chat_history.sql")

    # 3. 社区帖子
    print("\n[3/3] 生成社区帖子...")
    posts = generate_posts(50)

    all_text = " ".join([p["title"] + " " + p["content"] for p in posts])
    coverage = {k: all_text.count(k) for k in SYMPTOM_KEYWORDS}
    print(f"  帖子总数: {len(posts)}")
    print(f"  关键词覆盖:")
    for k, count in coverage.items():
        print(f"    {k}: {count}次 {'✓' if count >= 2 else '⚠️ 不足'}")

    export_json(posts, "posts_enhanced_50.json")
    export_sql("posts", posts, "posts_enhanced_50.sql")

    print("\n" + "=" * 50)
    print("全部生成完毕")
    print("=" * 50)
