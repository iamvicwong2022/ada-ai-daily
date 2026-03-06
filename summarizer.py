"""
AI 摘要 + Ada 点评模块

两步流程:
1. 评估文章价值 (过滤纯功能发布)
2. 生成中文摘要 + Ada 风格点评
"""
import time
import logging
import re
import json

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL, SUMMARY_MAX_TOKENS

logger = logging.getLogger(__name__)

# Gemini 客户端 (延迟初始化)
_client = None


def _get_client():
    """获取 Gemini 客户端 (单例)"""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY 未设置！请在 .env 文件中配置。")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


# ============================================================
# Prompt: 内容价值评估 + Ada 点评 (合并为一次 API 调用)
# ============================================================

EVALUATE_AND_COMMENT_PROMPT = """你需要同时完成两个任务: 评估这篇文章的价值，以及用 Ada 的身份写点评。

## 任务一: 价值评估

根据以下标准给文章打分 (1-5):
- 5分: 包含可直接应用的实践方法、效率提升技巧、或深度技术洞察
- 4分: 分享一线经验、产品设计思路、或前沿趋势的深度分析
- 3分: 有一定参考价值的行业动态或研究进展
- 2分: 单纯的产品功能发布、版本更新公告
- 1分: 营销内容、水文、标题党

过滤规则:
- 纯功能发布 (如 "我们发布了 XX 的新版本") → 2分
- 有实践分享 (如 "我用 XX 做了 YY，发现...") → 4-5分
- 深度技术解读 (如 "XX 背后的原理是...") → 4-5分
- 产品设计理念 (如 "为什么我们这样设计...") → 4分

## 任务二: Ada 点评

Ada 是一位在硅谷工作的华人 AI 产品经理，她的特点:
- 用 Builder 的视角看问题: "这对你有什么用？"
- 每条点评给出一个具体的行动建议或关键 takeaway
- 语气像一个懂技术的朋友在微信里跟你聊天
- 简洁有力，不说废话，中英文混用很自然
- 偶尔用 "试试..." "你可以..." "关键是..." 这样的句式

## 输入

文章标题: {title}
文章来源: {source}
文章内容:
{content}

## 输出格式 (严格 JSON)

```json
{{
  "score": 数字1-5,
  "summary": "2-3句中文摘要，保留关键英文术语",
  "ada_comment": "Ada 的一段话，40-80字，给出行动建议或关键洞察"
}}
```

直接输出 JSON，不要添加任何其他内容:"""


def _clean_html(text):
    """移除 HTML 标签"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:2000]


def _parse_response(text):
    """解析 Gemini 返回的 JSON"""
    # 尝试直接解析
    text = text.strip()
    # 移除可能的 markdown 代码块标记
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试从文本中提取 JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def evaluate_and_comment(title, content, source_name=""):
    """
    评估文章价值 + 生成 Ada 点评 (一次 API 调用)

    Returns:
        dict: {"score": int, "summary": str, "ada_comment": str}
        None: 如果 API 调用失败
    """
    client = _get_client()
    cleaned_content = _clean_html(content)

    prompt = EVALUATE_AND_COMMENT_PROMPT.format(
        title=title,
        source=source_name,
        content=cleaned_content if cleaned_content else "(无内容摘要)"
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "max_output_tokens": SUMMARY_MAX_TOKENS,
                "temperature": 0.4,
            }
        )

        result = _parse_response(response.text)
        if result and isinstance(result.get("score"), (int, float)):
            logger.info(
                f"[评估] {title[:40]}... → "
                f"分数={result['score']}, "
                f"Ada: {result.get('ada_comment', '')[:40]}..."
            )
            return result
        else:
            logger.warning(f"[解析失败] {title}: 返回内容不是有效 JSON")
            return None

    except Exception as e:
        logger.error(f"[API 失败] {title}: {e}")
        return None


def process_articles(articles, min_score=3, delay=1.5):
    """
    批量处理文章: 评估 + Ada 点评 + 过滤

    Args:
        articles: 文章列表
        min_score: 最低分数阈值 (低于此分的文章被过滤)
        delay: API 调用间隔 (秒)

    Returns:
        过滤后的文章列表 (带 chinese_summary 和 ada_comment)
    """
    total = len(articles)
    kept = []
    filtered_out = 0

    for i, article in enumerate(articles):
        logger.info(f"正在评估 ({i+1}/{total}): {article['title'][:60]}")

        result = evaluate_and_comment(
            title=article["title"],
            content=article.get("summary", ""),
            source_name=article.get("source_name", "")
        )

        if result:
            score = result.get("score", 0)
            if score >= min_score:
                article["chinese_summary"] = result.get("summary", "")
                article["ada_comment"] = result.get("ada_comment", "")
                article["value_score"] = score
                kept.append(article)
            else:
                filtered_out += 1
                logger.info(f"  ↳ 过滤 (分数={score}): {article['title'][:50]}")
        else:
            # API 失败时保留文章但不加点评
            article["chinese_summary"] = ""
            article["ada_comment"] = ""
            article["value_score"] = 0
            kept.append(article)

        # 速率控制
        if i < total - 1:
            time.sleep(delay)

    logger.info(f"✅ 评估完成: 保留 {len(kept)} 篇, 过滤 {filtered_out} 篇")

    # 按价值分数排序 (高分在前)
    kept.sort(key=lambda a: (-a.get("value_score", 0),))

    return kept


# 向后兼容 V1 接口
def summarize_batch(articles, delay=1.0):
    """V1 兼容: 仅生成摘要"""
    return process_articles(articles, min_score=1, delay=delay)
