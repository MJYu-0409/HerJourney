SYMPTOM_KEYS = [
    # 血管舒缩症状
    "hot_flash",       # 潮热
    "night_sweat",     # 夜间盗汗
    "palpitation",     # 心慌心悸
    # 精神情绪症状
    "mood_swing",      # 烦躁易怒
    "anxiety",         # 焦虑紧张
    "depression",      # 情绪低落
    "concentration",   # 注意力涣散
    # 睡眠障碍
    "sleep_onset",     # 入睡困难
    "sleep_wake",      # 夜间易醒
    "early_wake",      # 早醒
    # 泌尿生殖 & 骨骼躯体
    "vaginal_dryness", # 阴道干涩
    "urinary_urgency", # 尿频尿急
    "uti",             # 反复尿路感染
    "joint_pain",      # 关节骨骼酸痛
    "fatigue",         # 乏力疲惫
]

SYMPTOM_NAMES_ZH: dict[str, str] = {
    "hot_flash":       "潮热",
    "night_sweat":     "夜间盗汗",
    "palpitation":     "心慌心悸",
    "mood_swing":      "烦躁易怒",
    "anxiety":         "焦虑紧张",
    "depression":      "情绪低落",
    "concentration":   "注意力涣散",
    "sleep_onset":     "入睡困难",
    "sleep_wake":      "夜间易醒",
    "early_wake":      "早醒",
    "vaginal_dryness": "阴道干涩",
    "urinary_urgency": "尿频尿急",
    "uti":             "反复尿路感染",
    "joint_pain":      "关节骨骼酸痛",
    "fatigue":         "乏力疲惫",
}

SYMPTOM_TAGS_ZH: dict[str, str] = {k: f"#{v}" for k, v in SYMPTOM_NAMES_ZH.items()}

MENOPAUSE_STAGE_ZH = {
    "perimenopause": "围绝经期",
    "postmenopause": "绝经后",
    "unknown": "未知",
}

MEDICATION_OPTIONS = [
    "中药调理", "激素治疗", "钙片/维生素", "助眠药物", "其他",
]
