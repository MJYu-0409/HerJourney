"""
生成社区经验贴 Mock 数据

设计原则：
1. 按"用户画像"生成不同风格的帖子，Demo 时点进去不像假数据
2. 官方科普帖必须有权威感，普通用户帖要有真实感
3. 帖子分布要合理：官方科普置顶 + 经验帖居多 + 症状报告穿插
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent / "mock_data"

# ============ 用户画像库 ============
USER_PROFILES = [
    {"nickname": "静姐_48", "stage": "围绝经期", "style": "理性干货型"},
    {"nickname": "小花的妈妈", "stage": "围绝经期", "style": "情绪倾诉型"},
    {"nickname": "李女士", "stage": "绝经后", "style": "经验分享型"},
    {"nickname": "健康快乐", "stage": "围绝经期", "style": "积极鼓励型"},
    {"nickname": "夜半听雨", "stage": "围绝经期", "style": "文艺细腻型"},
    {"nickname": " she伴官方", "stage": None, "style": "官方科普型", "is_official": True},
]

# ============ 帖子内容模板库 ============
POST_TEMPLATES = {
    "experience": [
        {
            "title": "潮热盗汗三个月后，我终于找到了缓解方法",
            "content": """从去年秋天开始，潮热和盗汗突然找上门来。最严重的时候，一天要换两三件衣服，晚上更是睡不安稳。

我试过好几种方法，最后发现这三招对我最有效：

1. 穿分层衣服：棉质打底+薄外套，热的时候能快速脱掉
2. 睡前泡脚：用40度左右的温水泡15分钟，反而能让身体更容易降温
3. 饮食调整：少喝咖啡和酒，多吃豆制品

现在三个月过去了，虽然还会潮热，但频率和强度都明显降低了。姐妹们不要慌，这是一个可以管理的过程。""",
            "tags": ["#潮热", "#盗汗", "#经验分享", "#围绝经期"],
        },
        {
            "title": "失眠的日子，我是怎么熬过来的",
            "content": """更年期失眠真的太折磨人了。以前躺下就能睡着，现在半夜两三点眼睛还睁得大大的。

分享一下我的"睡眠修复计划"：

- 固定作息：不管几点睡着，早上七点准时起床
- 午睡控制：最多20分钟，下午三点后不再睡
- 卧室改造：换了遮光窗帘，买了白噪音机
- 放松训练：睡前做渐进式肌肉放松

最重要的，是接受"现在睡眠质量不如以前"这个事实。不焦虑，反而更容易睡着。""",
            "tags": ["#睡眠障碍", "#失眠", "#情绪管理", "#围绝经期"],
        },
        {
            "title": "给刚进入更年期的姐妹：这些症状都是正常的",
            "content": """48岁那年，我第一次出现潮热的时候，以为自己得了什么大病。跑了好几次医院，检查结果都是"正常"。

后来我才慢慢了解，这些都是更年期的正常表现：
- 突然的潮热和出汗
- 情绪波动，容易烦躁
- 记忆力下降，忘东忘西
- 睡眠质量变差
- 关节疼痛

知道这是正常的，心理压力就小了很多。现在我用"她伴"每天记录症状，看着数据慢慢变化，心里有底多了。""",
            "tags": ["#更年期", "#科普", "#新手指南", "#围绝经期"],
        },
    ],
    "report": [
        {
            "title": "我的30天症状报告：潮热改善明显",
            "content": """连续打卡30天后，生成了我的第一份症状报告。

数据显示：
- 潮热：从平均4.2分降到2.1分 ⬇️
- 盗汗：从3.8分降到1.9分 ⬇️
- 睡眠：从4.5分降到2.8分 ⬇️
- 情绪：基本稳定在3分左右

AI 解读说我的心血管相关症状呈现明显下降趋势，建议继续保持当前的作息和运动习惯。

把这份报告分享到社区，希望能给有类似症状的姐妹一些参考。""",
            "tags": ["#症状报告", "#潮热", "#数据记录", "#围绝经期"],
        },
        {
            "title": "围绝经期第一个月的数据记录",
            "content": """刚开始用小程序记录症状，第一个月的数据出来了。

整体来看，我的症状集中在几个方面：
1. 心血管：潮热和盗汗比较严重
2. 情绪：烦躁和焦虑交替出现
3. 睡眠：入睡困难，容易早醒

通过记录发现，经期前后症状会加重，这是一个规律。下个月准备重点调整饮食，看看能不能有改善。""",
            "tags": ["#症状报告", "#围绝经期", "#数据记录"],
        },
    ],
    "general": [
        {
            "title": "今天去医院做了骨密度检查",
            "content": "医生建议围绝经期女性每年做一次骨密度检查，今天去做了，结果正常。医生说要多补钙、多晒太阳、适当运动。姐妹们有定期检查吗？",
            "tags": ["#骨骼健康", "#医院检查", "#围绝经期"],
        },
        {
            "title": "有没有推荐的更年期保健品？",
            "content": "最近想补充一些营养素，大豆异黄酮和钙片是必买的，还在考虑要不要加维生素D。姐妹们有什么推荐或者踩坑经验吗？",
            "tags": ["#保健品", "#求助", "#围绝经期"],
        },
    ],
    "official": [
        {
            "title": "【科普】什么是围绝经期？",
            "content": """围绝经期（Perimenopause）是指女性从生育期过渡到绝经期的阶段，通常发生在45-55岁之间。

主要特征：
- 月经周期开始变得不规律
- 雌激素水平波动和下降
- 出现各种身体和心理症状

常见症状包括潮热、盗汗、情绪波动、睡眠障碍等。

围绝经期通常持续2-8年，最后连续12个月没有月经即为绝经。

本内容仅供健康参考，不构成医疗建议。如有疑问请咨询专业医生。""",
            "tags": ["#官方科普", "#围绝经期", "#基础知识"],
        },
        {
            "title": "【科普】激素替代疗法（HRT）安全吗？",
            "content": """激素替代疗法（HRT）是缓解更年期症状的有效手段之一，但并非适合所有人。

适用人群：
- 症状严重影响生活质量
- 无乳腺癌、血栓等禁忌症
- 在医生指导下使用

注意事项：
- 需在专业医生评估后使用
- 定期复查，调整剂量
- 短期使用风险较低

是否使用 HRT 是一个需要与医生共同决策的问题。""",
            "tags": ["#官方科普", "#激素替代疗法", "#医疗建议"],
        },
    ],
}


def random_time_ago(base_time: datetime) -> str:
    """生成相对时间描述"""
    delta = base_time - datetime.now()
    minutes = int(-delta.total_seconds() / 60)

    if minutes < 5:
        return "刚刚"
    elif minutes < 60:
        return f"{minutes}分钟前"
    elif minutes < 24 * 60:
        return f"{minutes // 60}小时前"
    elif minutes < 48 * 60:
        return "昨天"
    else:
        return f"{minutes // (24 * 60)}天前"


def generate_posts(count: int = 12) -> list[dict]:
    """生成帖子列表"""
    posts = []
    now = datetime.now()

    # 官方科普帖必须置顶（时间最新）
    for tmpl in POST_TEMPLATES["official"]:
        posts.append(create_post(tmpl, USER_PROFILES[-1], now))

    # 其他类型帖子按时间倒序分布
    other_templates = (
        POST_TEMPLATES["experience"] * 2
        + POST_TEMPLATES["report"] * 2
        + POST_TEMPLATES["general"] * 2
    )
    random.shuffle(other_templates)

    for i, tmpl in enumerate(other_templates[:count]):
        profile = random.choice(USER_PROFILES[:-1])  # 排除官方
        # 时间分布：越新的帖子时间越近
        time_offset = timedelta(
            minutes=random.randint(i * 60, (i + 1) * 120)
        )
        post_time = now - time_offset
        posts.append(create_post(tmpl, profile, post_time))

    # 按时间倒序排列
    posts.sort(key=lambda x: x["created_at"], reverse=True)
    return posts


def create_post(template: dict, profile: dict, post_time: datetime) -> dict:
    """创建单条帖子数据"""
    post_type = "official" if profile.get("is_official") else {
        "experience": "experience",
        "report": "report",
        "general": "general",
    }.get(next((k for k, v in POST_TEMPLATES.items() if template in v), "general"))

    is_official = profile.get("is_official", False)
    views = random.randint(50, 2000) if not is_official else random.randint(1000, 5000)
    likes = int(views * random.uniform(0.05, 0.15))
    comments = int(views * random.uniform(0.02, 0.08))

    return {
        "id": str(uuid.uuid4()),
        "user_id": None if is_official else f"user-{random.randint(1000, 9999)}",
        "post_type": post_type,
        "title": template["title"],
        "content": template["content"],
        "images": None,
        "voice_url": None,
        "tags": json.dumps(template["tags"], ensure_ascii=False),
        "is_ai_generated": False,
        "status": "published",
        "likes": likes,
        "views": views,
        "created_at": post_time.isoformat(),
        "published_at": post_time.isoformat(),
        # 以下为展示用字段（非数据库字段）
        "_nickname": profile["nickname"],
        "_stage": profile["stage"],
        "_time_ago": random_time_ago(post_time),
    }


def export_as_json(posts: list[dict]) -> None:
    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / "mock_posts.json"

    # 分离数据库字段和展示字段
    db_posts = []
    display_posts = []
    for p in posts:
        db_posts.append({k: v for k, v in p.items() if not k.startswith("_")})
        display_posts.append({
            "title": p["title"],
            "content_preview": p["content"][:80] + "..." if len(p["content"]) > 80 else p["content"],
            "author": p["_nickname"],
            "stage": p["_stage"],
            "time_ago": p["_time_ago"],
            "tags": json.loads(p["tags"]),
            "likes": p["likes"],
            "views": p["views"],
            "post_type": p["post_type"],
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "db_format": db_posts,
            "display_format": display_posts,
        }, f, ensure_ascii=False, indent=2)
    print(f"已生成 {len(posts)} 条帖子数据 → {path}")


def export_as_sql(posts: list[dict]) -> None:
    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / "mock_posts.sql"

    lines = [
        "-- 社区帖子 Mock 数据",
        "DELETE FROM posts WHERE user_id IS NOT NULL;  -- 保留可能的官方帖",
        "",
    ]
    for p in posts:
        # 跳过 user_id 为 None 的（官方帖），因为 SQL 中需要特殊处理
        if p["user_id"] is None:
            continue
        cols = ["id", "user_id", "post_type", "title", "content", "images",
                "voice_url", "tags", "is_ai_generated", "status", "likes", "views", "created_at", "published_at"]
        vals = [
            f"'{p['id']}'",
            f"'{p['user_id']}'",
            f"'{p['post_type']}'",
            "'" + p['title'].replace("'", "''") + "'",
            "'" + p['content'].replace("'", "''") + "'",
            "NULL",
            "NULL",
            f"'{p['tags']}'",
            "false",
            f"'{p['status']}'",
            str(p["likes"]),
            str(p["views"]),
            f"'{p['created_at']}'",
            f"'{p['published_at']}'",
        ]
        lines.append(f"INSERT INTO posts ({', '.join(cols)}) VALUES ({', '.join(vals)});")

    # 官方帖单独处理（user_id 为 NULL）
    for p in posts:
        if p["user_id"] is not None:
            continue
        cols = ["id", "user_id", "post_type", "title", "content", "images",
                "voice_url", "tags", "is_ai_generated", "status", "likes", "views", "created_at", "published_at"]
        vals = [
            f"'{p['id']}'",
            "NULL",
            f"'{p['post_type']}'",
            "'" + p['title'].replace("'", "''") + "'",
            "'" + p['content'].replace("'", "''") + "'",
            "NULL",
            "NULL",
            f"'{p['tags']}'",
            "false",
            f"'{p['status']}'",
            str(p["likes"]),
            str(p["views"]),
            f"'{p['created_at']}'",
            f"'{p['published_at']}'",
        ]
        lines.append(f"INSERT INTO posts ({', '.join(cols)}) VALUES ({', '.join(vals)});")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"已生成 SQL → {path}")


if __name__ == "__main__":
    posts = generate_posts(count=10)
    export_as_json(posts)
    export_as_sql(posts)

    print(f"\n帖子分布：")
    type_count = {}
    for p in posts:
        t = p["post_type"]
        type_count[t] = type_count.get(t, 0) + 1
    for t, c in type_count.items():
        print(f"  {t}: {c}条")
