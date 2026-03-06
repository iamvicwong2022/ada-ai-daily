"""
简报格式化模块 V2 — Ada 风格每日简报
"""
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from sources import CATEGORY_LABELS, CATEGORY_ORDER


def format_daily_digest(articles):
    """
    生成 Ada 风格的 Markdown 每日简报

    Returns:
        (title, body) 元组
    """
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    date_str = now.strftime("%Y.%m.%d")

    title = f"🧠 Ada AI 日报 — {date_str}"

    if not articles:
        body = (
            "今日 Ada 没有发现值得推荐的内容。\n\n"
            "可能是各大 AI 公司和 Builder 们今天都在埋头写代码 😄"
        )
        return title, body

    # 按分类分组
    grouped = defaultdict(list)
    for article in articles:
        cat = article.get("source_category", "company")
        grouped[cat].append(article)

    # 构建 Markdown 正文
    lines = []
    lines.append("> *Follow Builders, Not Influencers — Zara Zhang*\n")

    item_num = 1

    for category in CATEGORY_ORDER:
        if category not in grouped:
            continue

        label = CATEGORY_LABELS.get(category, category)
        lines.append(f"\n## {label}\n")

        for article in grouped[category]:
            eng_title = article.get("title", "Untitled")
            link = article.get("link", "")
            source = article.get("source_name", "")
            summary = article.get("chinese_summary", "")
            ada = article.get("ada_comment", "")
            score = article.get("value_score", 0)

            # 价值星标
            stars = "⭐" * min(score, 5) if score else ""

            # 格式化每条文章
            lines.append(f"**{item_num}. [{eng_title}]({link})** {stars}")
            lines.append(f"> 📍 {source}")

            if summary:
                lines.append(f"> 📝 {summary}")

            if ada:
                lines.append(f">")
                lines.append(f"> 💬 **Ada**: {ada}")

            lines.append("")  # 空行分隔
            item_num += 1

    # 页脚
    lines.append("---")
    lines.append(
        f"*📅 {date_str} | Ada AI 日报 · "
        f"为 Builder 精选的 AI 资讯*"
    )

    body = "\n".join(lines)
    return title, body


def format_test_message():
    """生成一条测试消息"""
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)

    title = "🧠 Ada AI 日报 — 测试消息"
    body = f"""## ✅ 连接测试成功！

> *Follow Builders, Not Influencers*

Server酱推送通道工作正常。

**测试时间**: {now.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)

从明天起，Ada 将每天为你精选最有价值的 AI 资讯，
过滤噪音，只推送对你真正有用的内容。

💬 **Ada**: 准备好了！我会帮你盯着硅谷一线 Builder 们在做什么，
你只需要每天花 3 分钟看我的推送就够了。

---
*Ada AI 日报 · 为 Builder 精选的 AI 资讯*"""

    return title, body
