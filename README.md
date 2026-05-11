# HerJourney 她伴

围绝经期健康管理微信小程序 Demo，包含症状打卡、AI 解读、社区分享三个核心功能。

---

## 项目结构

```
HerJourney/
├── backend/          # FastAPI 后端
│   ├── main.py       # 启动入口、DB 初始化、Mock 数据种子
│   ├── models.py     # SQLAlchemy ORM 模型
│   ├── schemas.py    # Pydantic 数据结构
│   ├── config.py     # 环境变量读取
│   ├── database.py   # DB 会话工厂
│   ├── routers/      # API 路由（user / survey / chat / profile / report / community）
│   ├── services/     # 业务逻辑（qwen.py AI 对话、report_builder.py 报告生成）
│   ├── mock_data/    # 90 天 Mock 调查数据（JSON）
│   └── .env.example  # 环境变量模板
├── frontend/         # 微信小程序
│   ├── app.json      # 页面路由 & TabBar 配置
│   ├── app.wxss      # 全局 CSS 变量（品牌色 #8E7AB5）
│   ├── pages/
│   │   ├── splash/   # 启动引导页
│   │   ├── daily/    # 今日打卡
│   │   ├── chat/     # AI 小伴对话
│   │   ├── community/# 社区「她说」
│   │   ├── profile/  # 个人中心
│   │   └── report/   # 症状旅程（图表 + AI 解读 + 分享）
│   ├── components/
│   │   ├── line-chart/   # 折线图自定义组件
│   │   └── chat-input/   # 聊天输入框组件
│   └── utils/api.js  # 统一 HTTP 请求封装
└── docs/             # 产品文档
```

---

## 环境要求

| 工具           | 版本              |
| -------------- | ----------------- |
| Python         | 3.10+             |
| 微信开发者工具 | 最新稳定版        |
| DashScope 账号 | 用于 Qwen AI 调用 |

---

## 本地启动

### 1. 克隆并配置环境变量

```bash
git clone <repo-url>
cd HerJourney/backend
cp .env.example .env
```

编辑 `.env`，填入你的 DashScope API Key：

```env
QWEN_API_KEY=sk-你的密钥
QWEN_MODEL=qwen-turbo
```

### 2. 安装依赖并启动后端

```bash
cd backend
python -m venv ../venv
../venv/Scripts/activate      # Windows
# source ../venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --port 5000 --reload
```

后端启动后访问 `http://127.0.0.1:5000/docs` 可查看 Swagger 接口文档。

> **注意（Windows）**：端口 8000 可能被 Hyper-V 占用，建议使用 5000。

### 3. 启动前端

1. 打开「微信开发者工具」
2. 导入 `frontend/` 目录
3. AppID 填写你的小程序 AppID（或使用测试号）
4. 确认 `frontend/utils/api.js` 中 `BASE_URL` 为 `http://127.0.0.1:5000`

---

## 主要功能

### 今日打卡（daily）

- 整体状态评分（5 档）
- 症状分类选择 + 严重程度打分
- 经期专项记录（经量、痛经、经血异常）
- 用药 / 干预记录
- 每周补充记录（体重、血压、关节、性生活）

### AI 小伴（chat）

- 基于 Qwen `qwen-turbo` 的多轮对话
- 历史会话管理

### 症状旅程（report）

- 近 7 / 14 / 30 / 90 日折线图（支持自定义日期）
- 症状切换 Picker
- AI 发现：基于打卡数据自动生成健康解读
- 分享旅程：将图表 + AI 发现 + 个人感受发布到社区

### 社区（community）

- 浏览她人分享的症状故事
- 点赞互动

### 个人中心（profile）

- 修改昵称 / 头像
- 查看个人信息

---

## API 概览

| 方法 | 路径                               | 说明           |
| ---- | ---------------------------------- | -------------- |
| POST | `/api/survey`                    | 提交今日打卡   |
| GET  | `/api/survey/history`            | 获取打卡历史   |
| GET  | `/api/report/chart`              | 症状折线图数据 |
| GET  | `/api/report/ai`                 | AI 健康解读    |
| POST | `/api/chat`                      | AI 对话        |
| GET  | `/api/chat/sessions`             | 会话列表       |
| GET  | `/api/community/posts`           | 社区帖子列表   |
| POST | `/api/community/posts`           | 发布分享       |
| POST | `/api/community/posts/{id}/like` | 点赞           |
| GET  | `/api/user/me`                   | 获取用户信息   |
| PUT  | `/api/user/me`                   | 更新昵称       |
| POST | `/api/user/avatar`               | 上传头像       |

---

## 开发说明

### Git 工作流

本地文件（`.env`、`*.db`、`project.private.config.json`）已加入 `.gitignore`，拉取新代码时不会产生冲突。

```bash
# 保留本地改动拉取最新代码
git stash
git pull
git stash pop
```

### Mock 数据

后端启动时自动从 `mock_data/survey_enhanced_90d.json` 导入 90 天的模拟打卡数据，无需手动操作。

### 微信开发者工具缓存

若页面改动未生效，按 `Ctrl + Shift + R` 强制重新编译。

---

## 技术栈

**后端**：FastAPI · SQLAlchemy 2.x · SQLite · Pydantic v2 · DashScope Qwen API

**前端**：微信小程序原生（WXML / WXSS / JS）

---

## 许可

本项目为 Demo 原型，仅供学习与展示使用。
