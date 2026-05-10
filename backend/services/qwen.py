import httpx
from openai import OpenAI
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL,
            http_client=httpx.Client(proxy=None),  # bypass system proxy to avoid SDK TypeError
        )
    return _client


CHAT_SYSTEM_PROMPT = """你是「HerJourney」的AI伴侣，专注陪伴围绝经期（更年期）女性。

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
- 末尾加注：*本回答仅供健康参考，不构成医疗建议*"""


def chat_completion(messages: list[dict], temperature: float = 0.7, max_tokens: int = 600) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=QWEN_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def build_chat_messages(history: list[dict], user_content: str) -> list[dict]:
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_content})
    return messages


_TREND_ZH = {"improving": "下降（好转）", "worsening": "上升（加重）", "stable": "平稳"}


def generate_report_interpretation(symptom_blocks: list[dict], days: int) -> str:
    """
    symptom_blocks: [{"name": "潮热", "avg": 3.2, "trend": "improving",
                       "data_text": "2025-04-10: 3\n..."}, ...]
    """
    period = f"过去{days}天" if days > 0 else "历史全部数据"
    lines = []
    for b in symptom_blocks:
        trend_zh = _TREND_ZH.get(b["trend"], b["trend"])
        lines.append(
            f"【{b['name']}】均值 {b['avg']:.1f} 分，整体趋势：{trend_zh}\n{b['data_text']}"
        )
    symptom_section = "\n\n".join(lines)

    prompt = f"""以下是用户{period}各症状的严重程度记录（1轻度-5严重）：

{symptom_section}

请用温暖专业的语气，对以上症状进行综合解读（200-300字）：
1. 各症状的整体趋势（哪些在好转 / 加重 / 平稳）
2. 症状之间可能的关联（例如睡眠差影响情绪等）
3. 值得关注的时间节点（如有明显波动）
4. 针对性的应对建议（2-3条实用建议）
5. 一句温暖的鼓励

只输出解读正文，不要加额外标题。
末尾另起一行加注：*本回答仅供健康参考，不构成医疗建议*"""

    messages = [{"role": "user", "content": prompt}]
    return chat_completion(messages, temperature=0.6, max_tokens=800)
