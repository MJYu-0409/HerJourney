# HerJourney — 后端开发 PRD

> Demo 版本 · v0.4  
> 技术栈：Python · FastAPI · SQLite（Demo）/ PostgreSQL（生产） · SQLAlchemy 2.x · Pydantic v2 · Qwen API

---

## 目录

1. [项目结构](#1-项目结构)
2. [环境与配置](#2-环境与配置)
3. [数据库模型](#3-数据库模型)
4. [模块一：用户（Mock）](#4-模块一用户mock)
5. [模块二：每日情况问卷](#5-模块二每日情况问卷)
6. [模块三：AI 问答](#6-模块三ai-问答)
7. [模块四：个人主页](#7-模块四个人主页)
8. [模块五：社区](#8-模块五社区)
9. [错误规范](#9-错误规范)
10. [开发优先级](#10-开发优先级)

---

## 1. 项目结构

```
backend/
├── main.py                  # FastAPI 入口，挂载路由，CORS，Static
├── database.py              # 数据库连接、Session 依赖
├── models.py                # SQLAlchemy ORM 模型
├── schemas.py               # Pydantic 请求/响应模型
├── config.py                # 环境变量读取（.env）
├── constants.py             # 症状枚举、中文名映射
├── routers/
│   ├── user.py              # 用户信息
│   ├── survey.py            # 每日问卷
│   ├── chat.py              # AI 问答
│   ├── profile.py           # 个人主页统计
│   ├── report.py            # 经验贴 / 症状报告生成
│   └── community.py         # 社区列表 / 搜索 / 分享
└── services/
    ├── qwen.py              # Qwen API 封装 + System Prompt
    └── report_builder.py    # 数据聚合、Prompt 构建工具
```

---

## 2. 环境与配置

### 2.1 依赖安装

```bash
pip install fastapi uvicorn sqlalchemy alembic pydantic[email] \
            python-dotenv openai python-multipart aiofiles
```

### 2.2 .env 变量

```env
# SQLite（Demo）
DATABASE_URL=sqlite:///./herjourney.db

# 生产切换 PostgreSQL：
# DATABASE_URL=postgresql://user:pass@localhost:5432/herjourney

QWEN_API_KEY=sk-xxx
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus

UPLOAD_DIR=static/uploads
```

### 2.3 启动

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2.4 认证（Demo）

所有接口从 Header `X-User-Id` 读取用户 ID，无需真实登录。
Demo 固定 Mock 用户 ID：`mock-user-001`。

---

## 3. 数据库模型

### users

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | UUID |
| openid | VARCHAR(64) NULL | 微信 openid |
| nickname | VARCHAR(50) | 昵称 |
| birth_year | SMALLINT NULL | |
| menopause_stage | VARCHAR(20) | perimenopause / postmenopause / unknown |
| created_at | TIMESTAMP | |

### daily_surveys

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | |
| user_id | VARCHAR(36) FK | |
| survey_date | DATE | 唯一约束：(user_id, survey_date) |
| menstrual_status | VARCHAR(20) | none / ongoing / ended_this_cycle |
| menstrual_day | SMALLINT NULL | 经期第几天 |
| menstrual_flow | SMALLINT NULL | 血量 1–5 |
| menstrual_pain | SMALLINT NULL | 痛经 0–5 |
| menstrual_abnormal | JSON NULL | 异常 tag 数组 |
| symptoms | JSON | `{"hot_flash":3,"night_sweat":0,...}` |
| overall_score | SMALLINT NULL | 整体状态 1–5 |
| notes | TEXT NULL | |
| created_at | TIMESTAMP | |

**症状字段 key 枚举**（心血管 / 骨骼 / 泌尿 / 神经 / 情绪 / 皮肤）

```
hot_flash, night_sweat, palpitation, chest_tightness
joint_stiffness, bone_pain, muscle_ache, fatigue
urinary_freq, urinary_leak, vaginal_dryness, pain_intercourse
memory_decline, concentration, headache
irritable, anxiety, depression, sleep_disorder
skin_dry, hair_loss, weight_change
```

### chat_messages

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | |
| user_id | VARCHAR(36) FK | |
| session_id | VARCHAR(36) | 会话分组 |
| role | VARCHAR(10) | user / assistant |
| content | TEXT | |
| created_at | TIMESTAMP | |

### posts

| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) PK | |
| user_id | VARCHAR(36) FK NULL | NULL = 官方账号 |
| post_type | VARCHAR(20) | experience / symptom_report / general / official |
| title | VARCHAR(200) | |
| content | TEXT | |
| tags | JSON | tag 字符串数组，如 `["#潮热","#HerJourney"]` |
| report_data | JSON NULL | 症状报告专用：`{symptom_key, data_points:[{date,score}]}` |
| images | JSON NULL | 图片 URL 数组 |
| is_ai_generated | BOOLEAN | |
| status | VARCHAR(10) | draft / published |
| likes | INTEGER DEFAULT 0 | |
| views | INTEGER DEFAULT 0 | |
| created_at | TIMESTAMP | |
| published_at | TIMESTAMP NULL | |

---

## 4. 模块一：用户（Mock）

#### `GET /api/user/me`

**Response**
```json
{
  "id": "mock-user-001",
  "nickname": "小桃",
  "menopause_stage": "perimenopause",
  "birth_year": 1972
}
```

---

## 5. 模块二：每日情况问卷

### 接口

#### `POST /api/survey`

提交当日问卷，同日重复提交自动覆盖。

**Request Body**
```json
{
  "menstrual_status": "ongoing",
  "menstrual_day": 3,
  "menstrual_flow": 3,
  "menstrual_pain": 2,
  "menstrual_abnormal": ["blood_clot"],
  "symptoms": {
    "hot_flash": 4,
    "night_sweat": 2,
    "sleep_disorder": 3
  },
  "overall_score": 3,
  "notes": "今天还好"
}
```

**逻辑**：未传入的 symptom key 自动补 0。同日已有记录则 UPDATE，否则 INSERT。

**Response** `201`
```json
{ "id": "uuid", "survey_date": "2025-05-10", "message": "打卡成功" }
```

---

#### `GET /api/survey/today`

**Response**
```json
{ "completed": true, "survey_date": "2025-05-10", "overall_score": 3 }
```

---

#### `GET /api/survey/history`

**Query Params**：`days`（int，默认 30，可选 7/30/90）

**Response**
```json
{
  "records": [
    {
      "survey_date": "2025-05-01",
      "overall_score": 3,
      "symptoms": { "hot_flash": 2, "sleep_disorder": 4 },
      "menstrual_status": "none"
    }
  ]
}
```

---

## 6. 模块三：AI 问答

> Demo 版本：不接 RAG，直接用 Prompt 引导 Qwen 模拟知识库回答。
> 语音输入：Demo 阶段由前端调用微信 API 转文字后，以文本形式提交本接口。

### 接口

#### `POST /api/chat`

**Request Body**
```json
{
  "session_id": "uuid-or-null",
  "content": "最近老是潮热，怎么办？"
}
```

- `session_id` 为 null 时后端自动创建新会话

**Response**
```json
{
  "session_id": "uuid",
  "role": "assistant",
  "content": "我理解你的感受…",
  "created_at": "2025-05-10T10:00:00Z"
}
```

**逻辑**

1. 读取该 session 历史消息（最近 10 条）构建上下文
2. 写入用户消息
3. 调用 Qwen（temperature 0.7）
4. 写入 AI 回答并返回

**System Prompt**

```
你是「HerJourney」的AI伴侣，专注陪伴围绝经期（更年期）女性。

你同时扮演三个角色：
① 医学科普助手（基于权威更年期医学知识解答）
② 经验分享汇总者（结合其他姐妹的真实应对经验给建议）
③ 情感支持伙伴（先认同感受，再给建议）

【回答结构（必须按此顺序）】
1. 情绪认同（1-2句，真诚共情，不要公式化）
2. 科普解释（通俗语言，说清楚为什么会这样）
3. 应对建议（2-3条可操作的建议，参考医学指南和真实经验）
4. 温暖结尾（一句鼓励，让她感到不孤单）

【强制规则】
- 异常出血 / 胸痛 / 剧烈头痛 / 疑似骨折 → 必须建议及时就医
- 不给具体药物剂量推荐
- 200-300字以内
- 末尾加注：*本回答仅供健康参考，不构成医疗建议*
```

---

#### `GET /api/chat/sessions`

获取当前用户的所有会话列表。

**Response**
```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "first_message": "最近老是潮热...",
      "message_count": 4,
      "last_at": "2025-05-10T10:00:00Z"
    }
  ]
}
```

---

#### `GET /api/chat/history`

**Query Params**：`session_id`（required）

**Response**
```json
{
  "session_id": "uuid",
  "messages": [
    { "role": "user", "content": "...", "created_at": "..." },
    { "role": "assistant", "content": "...", "created_at": "..." }
  ]
}
```

---

## 7. 模块四：个人主页

> 包含两部分：① 统计大数字 ② 统一报告（多症状折线图 + AI 解读 + 可分享）

### 报告设计说明

经验贴与症状报告合并为**统一报告**，交互流程如下：

1. **默认视图**：展示所有历史数据中出现过的症状，多折线图（时间轴 x 轴，严重程度 y 轴 1-5），AI 生成全症状综合解读。
2. **用户筛选**：可修改时间段（7 / 30 / 90 天 / 自定义）、勾选关注的症状，重新调 AI 生成该次解读。
3. **保存分享**：每次生成的解读 + 对应的图表数据保存为一个 `draft` post，用户编辑后可分享到社区。

---

### 接口

#### `GET /api/profile/stats`

个人主页统计数字。

**Response**
```json
{
  "total_checkin_days": 45,
  "current_streak": 7,
  "total_ai_chats": 12,
  "avg_overall_score_30d": 3.2,
  "top_symptoms": [
    { "key": "hot_flash", "name": "潮热", "avg_score": 3.8, "days_reported": 30 },
    { "key": "sleep_disorder", "name": "睡眠障碍", "avg_score": 3.1, "days_reported": 25 }
  ]
}
```

---

#### `GET /api/report/chart`

获取图表原始数据（无 AI，用于交互式多折线图渲染）。

**Query Params**

| 参数 | 类型 | 说明 |
|------|------|------|
| days | int | 时间段，默认 90，传 0 = 全部历史 |
| symptoms | string | 逗号分隔的症状 key，不传 = 所有有数据的症状 |

**Response**
```json
{
  "since": "2025-02-09",
  "until": "2025-05-10",
  "symptoms": [
    {
      "key": "hot_flash",
      "name": "潮热",
      "data_points": [
        { "date": "2025-02-10", "score": 3 },
        { "date": "2025-02-12", "score": 4 }
      ],
      "avg_score": 3.2,
      "days_reported": 28,
      "trend": "improving"
    }
  ]
}
```

**trend 取值**：`improving`（下降） / `worsening`（上升） / `stable`（平稳）

---

#### `POST /api/report/generate`

根据选定时间段和症状，AI 生成综合解读报告，保存为草稿。

**Request Body**
```json
{
  "days": 30,
  "symptom_keys": ["hot_flash", "sleep_disorder"]
}
```

- `symptom_keys` 为空数组或不传 → 使用该时间段内所有有数据的症状
- `days` 为 0 → 使用全部历史数据

**逻辑**

1. 读取指定时间段内各症状评分序列
2. 计算每个症状的均值、趋势
3. 构建多症状 Prompt，调用 Qwen（temperature 0.6，max_tokens 800）
4. 将图表数据（`report_data`）+ AI 解读（`content`）存为 `post_type=report, status=draft`

**Prompt 要点**
```
以下是用户过去{days}天各症状的严重程度记录（1轻度-5严重）：

【{症状名1}】均值{avg}分，趋势{trend}，数据：{日期:分数...}
【{症状名2}】...

请用温暖专业的语气综合解读（200-300字）：
1. 各症状的整体趋势（哪些在好转/加重/平稳）
2. 症状间可能的关联（如睡眠影响情绪等）
3. 值得关注的时间节点
4. 给用户的针对性建议（2-3条）
5. 一句温暖的鼓励

末尾加注：*本回答仅供健康参考，不构成医疗建议*
```

**Response** `201`
```json
{
  "post_id": "uuid",
  "days": 30,
  "symptom_keys": ["hot_flash", "sleep_disorder"],
  "symptoms": [
    {
      "key": "hot_flash",
      "name": "潮热",
      "data_points": [{ "date": "2025-04-10", "score": 3 }],
      "avg_score": 3.2,
      "days_reported": 20,
      "trend": "improving"
    }
  ],
  "interpretation": "近30天，您的潮热症状整体呈下降趋势...",
  "tags": ["#潮热", "#睡眠障碍", "#HerJourney"],
  "status": "draft"
}
```

---

#### `GET /api/report/drafts`

获取用户所有草稿报告。

**Response**
```json
{
  "drafts": [
    {
      "post_id": "uuid",
      "post_type": "report",
      "title": "健康报告·潮热&睡眠障碍·近30天",
      "created_at": "2025-05-10T10:00:00Z"
    }
  ]
}
```

---

## 8. 模块五：社区

> 经验贴和症状报告草稿可由用户编辑内容后分享到社区，自动携带标签。

### 接口

#### `POST /api/community/share`

将草稿（或新建帖子）发布到社区。

**Request Body**
```json
{
  "post_id": "uuid-or-null",
  "post_type": "experience",
  "title": "我的30天更年期记录（编辑后）",
  "content": "...",
  "tags": ["#HerJourney", "#潮热"]
}
```

- `post_id` 非空：更新现有草稿内容并发布
- `post_id` 为 null：新建帖子并发布
- `published_at` 写入当前时间，`status` 更新为 `published`

**Response** `201`
```json
{ "post_id": "uuid", "status": "published", "published_at": "2025-05-10T10:00:00Z" }
```

---

#### `GET /api/community/posts`

帖子列表，支持 tab 筛选 / 关键词搜索 / tag 搜索。

**Query Params**

| 参数 | 类型 | 说明 |
|------|------|------|
| tab | string | all / experience / symptom_report / official，默认 all |
| keyword | string | 关键词（匹配 title + content） |
| tag | string | 精确 tag 筛选，如 `#潮热` |
| page | int | 默认 1 |
| page_size | int | 默认 10，最大 50 |

**Response**
```json
{
  "total": 42,
  "page": 1,
  "items": [
    {
      "id": "uuid",
      "post_type": "experience",
      "title": "我的30天更年期记录",
      "summary": "前80字摘要...",
      "tags": ["#潮热", "#HerJourney"],
      "author_nickname": "小桃",
      "is_official": false,
      "likes": 12,
      "views": 88,
      "published_at": "2025-05-10T08:00:00Z"
    }
  ]
}
```

**排序规则**：官方帖置顶，其余按 `published_at` 倒序。

---

#### `GET /api/community/posts/{post_id}`

帖子详情，同时 `views += 1`。

**Response**
```json
{
  "id": "uuid",
  "post_type": "experience",
  "title": "...",
  "content": "...",
  "tags": ["#潮热"],
  "report_data": null,
  "author_nickname": "小桃",
  "is_official": false,
  "likes": 12,
  "views": 89,
  "published_at": "..."
}
```

> 症状报告帖的 `report_data` 包含折线图数据，前端用于渲染图表。

---

#### `POST /api/community/posts/{post_id}/like`

点赞/取消点赞（Demo 不做持久化用户状态，仅 likes +1）。

**Response**
```json
{ "likes": 13 }
```

---

#### `GET /api/community/tags`

获取热门 tag 列表（按使用频率排序）。

**Query Params**：`limit`（int，默认 20）

**Response**
```json
{
  "tags": [
    { "name": "#潮热", "count": 35 },
    { "name": "#睡眠障碍", "count": 28 }
  ]
}
```

---

#### `POST /api/post/upload`

上传图片，返回可访问 URL（Demo 存本地 `static/uploads/`）。

**Request**：multipart/form-data，字段 `file`

**Response**
```json
{ "url": "/static/uploads/xxx.jpg", "type": "image" }
```

---

## 9. 错误规范

```json
{
  "error": "NOT_FOUND",
  "message": "帖子不存在",
  "status_code": 404
}
```

| code | status | 说明 |
|------|--------|------|
| NOT_FOUND | 404 | 资源不存在 |
| QWEN_API_ERROR | 502 | Qwen API 调用失败 |
| INVALID_PARAMS | 422 | 参数校验失败（Pydantic 自动） |
| FORBIDDEN | 403 | 无权操作他人帖子 |

---

## 10. 开发优先级

| 优先级 | 模块 | 接口 |
|--------|------|------|
| P0 | 每日问卷 | POST /survey · GET /survey/today · GET /survey/history |
| P0 | AI 问答 | POST /chat |
| P0 | 个人主页 | GET /profile/stats |
| P0 | 统一报告 | GET /report/chart · POST /report/generate · POST /community/share |
| P0 | 社区 | GET /community/posts · GET /community/posts/:id |
| P1 | AI 问答历史 | GET /chat/sessions · GET /chat/history |
| P1 | 社区搜索 | keyword / tag 筛选 |
| P1 | 标签热榜 | GET /community/tags |
| P1 | 文件上传 | POST /post/upload |
| P2 | 点赞 | POST /community/posts/:id/like |
| P1 | 草稿列表 | GET /report/drafts |

---

*HerJourney Backend PRD · Demo v0.3*
