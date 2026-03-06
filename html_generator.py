"""
HTML 日报生成器 — 生成精美的 Ada AI 日报网页

生成的 HTML 文件保存到 docs/ 目录，可直接部署到 GitHub Pages。
"""
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

from sources import CATEGORY_LABELS, CATEGORY_ORDER
from config import PROJECT_DIR

# HTML 输出目录
DOCS_DIR = PROJECT_DIR / "docs"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="Ada AI 日报 — 为 Builder 精选的 AI 资讯，Follow Builders Not Influencers">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0a0f;
            --bg-card: #12121a;
            --bg-card-hover: #1a1a26;
            --bg-ada: #1a1528;
            --border: #2a2a3a;
            --text-primary: #e8e8f0;
            --text-secondary: #8888a0;
            --text-ada: #c8b8f0;
            --accent-purple: #8b5cf6;
            --accent-blue: #3b82f6;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --star: #fbbf24;
            --gradient-1: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
            --gradient-2: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
            line-height: 1.7;
            min-height: 100vh;
        }}

        .container {{
            max-width: 720px;
            margin: 0 auto;
            padding: 24px 16px 60px;
        }}

        /* Header */
        .header {{
            text-align: center;
            padding: 40px 0 32px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 32px;
        }}

        .header-brand {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}

        .header-icon {{
            width: 40px;
            height: 40px;
            background: var(--gradient-1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
        }}

        .header-name {{
            font-size: 24px;
            font-weight: 700;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header-date {{
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}

        .header-tagline {{
            font-size: 13px;
            color: var(--text-secondary);
            font-style: italic;
            opacity: 0.7;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 20px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-num {{
            font-size: 22px;
            font-weight: 700;
            color: var(--accent-purple);
        }}

        .stat-label {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        /* Category Section */
        .category {{
            margin-bottom: 36px;
        }}

        .category-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
            letter-spacing: 0.5px;
        }}

        /* Article Card */
        .article {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 14px;
            transition: all 0.2s ease;
        }}

        .article:hover {{
            background: var(--bg-card-hover);
            border-color: var(--accent-purple);
            transform: translateY(-1px);
        }}

        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 10px;
        }}

        .article-title {{
            font-size: 16px;
            font-weight: 600;
            line-height: 1.4;
        }}

        .article-title a {{
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.2s;
        }}

        .article-title a:hover {{
            color: var(--accent-purple);
        }}

        .article-stars {{
            color: var(--star);
            font-size: 13px;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .article-source {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }}

        .article-summary {{
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.65;
            margin-bottom: 14px;
        }}

        /* Ada Comment */
        .ada-comment {{
            background: var(--bg-ada);
            border-left: 3px solid var(--accent-purple);
            border-radius: 0 8px 8px 0;
            padding: 12px 16px;
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-ada);
        }}

        .ada-label {{
            font-weight: 600;
            color: var(--accent-purple);
            margin-right: 4px;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding-top: 32px;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 13px;
        }}

        .footer a {{
            color: var(--accent-purple);
            text-decoration: none;
        }}

        /* Nav for archive */
        .nav {{
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-top: 16px;
        }}

        .nav a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 13px;
            padding: 6px 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            transition: all 0.2s;
        }}

        .nav a:hover {{
            color: var(--accent-purple);
            border-color: var(--accent-purple);
        }}

        /* Responsive */
        @media (max-width: 480px) {{
            .container {{ padding: 16px 12px 40px; }}
            .header {{ padding: 24px 0 20px; }}
            .header-name {{ font-size: 20px; }}
            .article {{ padding: 16px; }}
            .stats {{ gap: 16px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-brand">
                <div class="header-icon">🧠</div>
                <span class="header-name">Ada AI 日报</span>
            </div>
            <div class="header-date">{date_display}</div>
            <div class="header-tagline">Follow Builders, Not Influencers — Zara Zhang</div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-num">{article_count}</div>
                    <div class="stat-label">精选文章</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{source_count}</div>
                    <div class="stat-label">信息源</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{filtered_count}</div>
                    <div class="stat-label">已过滤</div>
                </div>
            </div>
        </header>

        {content}

        <footer class="footer">
            <p>Ada AI 日报 · 为 Builder 精选的 AI 资讯</p>
            <p style="margin-top: 8px;">由 Gemini API 驱动 · 灵感来自 Zara Zhang</p>
            <nav class="nav">
                <a href="./index.html">📋 目录</a>
            </nav>
        </footer>
    </div>
</body>
</html>"""


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ada AI 日报 — 存档</title>
    <meta name="description" content="Ada AI 日报历史存档 — 为 Builder 精选的 AI 资讯">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0a0f;
            --bg-card: #12121a;
            --bg-card-hover: #1a1a26;
            --border: #2a2a3a;
            --text-primary: #e8e8f0;
            --text-secondary: #8888a0;
            --accent-purple: #8b5cf6;
            --gradient-1: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
            line-height: 1.7;
            min-height: 100vh;
        }}
        .container {{ max-width: 620px; margin: 0 auto; padding: 24px 16px 60px; }}
        .header {{
            text-align: center;
            padding: 40px 0 32px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 32px;
        }}
        .header-brand {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}
        .header-icon {{
            width: 40px; height: 40px;
            background: var(--gradient-1);
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
        }}
        .header-name {{
            font-size: 24px; font-weight: 700;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header-tagline {{
            font-size: 13px; color: var(--text-secondary);
            font-style: italic; opacity: 0.7;
        }}
        .issue {{
            display: block;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 10px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.2s ease;
        }}
        .issue:hover {{
            background: var(--bg-card-hover);
            border-color: var(--accent-purple);
            transform: translateY(-1px);
        }}
        .issue-date {{ font-weight: 600; font-size: 15px; }}
        .issue-count {{ color: var(--text-secondary); font-size: 13px; margin-top: 2px; }}
        .footer {{
            text-align: center; padding-top: 32px;
            border-top: 1px solid var(--border);
            color: var(--text-secondary); font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-brand">
                <div class="header-icon">🧠</div>
                <span class="header-name">Ada AI 日报</span>
            </div>
            <div class="header-tagline">Follow Builders, Not Influencers</div>
        </header>

        <h2 style="font-size: 16px; color: var(--text-secondary); margin-bottom: 16px;">📚 历史日报</h2>

        {issues}

        <footer class="footer">
            <p>Ada AI 日报 · 为 Builder 精选的 AI 资讯</p>
        </footer>
    </div>
</body>
</html>"""


def _escape(text):
    """HTML 转义"""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def generate_html_digest(articles, filtered_count=0):
    """
    生成 HTML 格式的每日简报

    Args:
        articles: 处理后的文章列表
        filtered_count: 被过滤的文章数

    Returns:
        (filename, html_content, page_url_path) 元组
    """
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    date_str = now.strftime("%Y-%m-%d")
    date_display = now.strftime("%Y 年 %m 月 %d 日 · %A")
    filename = f"{date_str}.html"

    # 按分类分组
    grouped = defaultdict(list)
    sources_seen = set()
    for article in articles:
        cat = article.get("source_category", "company")
        grouped[cat].append(article)
        sources_seen.add(article.get("source_name", ""))

    # 生成文章内容
    content_parts = []

    for category in CATEGORY_ORDER:
        if category not in grouped:
            continue

        label = CATEGORY_LABELS.get(category, category)
        content_parts.append(f'<section class="category">')
        content_parts.append(f'<h2 class="category-title">{_escape(label)}</h2>')

        for article in grouped[category]:
            title = _escape(article.get("title", "Untitled"))
            link = _escape(article.get("link", "#"))
            source = _escape(article.get("source_name", ""))
            summary = _escape(article.get("chinese_summary", ""))
            ada = _escape(article.get("ada_comment", ""))
            score = article.get("value_score", 0)

            stars = "⭐" * min(score, 5) if score else ""

            content_parts.append('<div class="article">')
            content_parts.append('<div class="article-header">')
            content_parts.append(
                f'<div class="article-title">'
                f'<a href="{link}" target="_blank" rel="noopener">{title}</a>'
                f'</div>'
            )
            if stars:
                content_parts.append(f'<span class="article-stars">{stars}</span>')
            content_parts.append('</div>')

            content_parts.append(f'<div class="article-source">📍 {source}</div>')

            if summary:
                content_parts.append(f'<div class="article-summary">{summary}</div>')

            if ada:
                content_parts.append(
                    f'<div class="ada-comment">'
                    f'<span class="ada-label">💬 Ada:</span> {ada}'
                    f'</div>'
                )

            content_parts.append('</div>')

        content_parts.append('</section>')

    content = "\n".join(content_parts)

    html = HTML_TEMPLATE.format(
        title=f"Ada AI 日报 — {date_str}",
        date_display=date_display,
        article_count=len(articles),
        source_count=len(sources_seen),
        filtered_count=filtered_count,
        content=content,
    )

    # 确保目录存在
    DOCS_DIR.mkdir(exist_ok=True)

    # 写入文件
    filepath = DOCS_DIR / filename
    filepath.write_text(html, encoding="utf-8")

    # 更新索引页
    _update_index()

    return filename, html, f"./{filename}"


def _update_index():
    """更新 docs/index.html 索引页"""
    DOCS_DIR.mkdir(exist_ok=True)

    # 扫描已有日报文件
    html_files = sorted(
        [f for f in DOCS_DIR.glob("20*.html")],
        reverse=True
    )

    issues_parts = []
    for f in html_files[:90]:  # 最多显示 90 期
        date_str = f.stem
        issues_parts.append(
            f'<a class="issue" href="./{f.name}">'
            f'<div class="issue-date">📰 {date_str}</div>'
            f'</a>'
        )

    if not issues_parts:
        issues_parts.append(
            '<p style="color: var(--text-secondary); text-align: center;">'
            '暂无日报</p>'
        )

    html = INDEX_TEMPLATE.format(issues="\n".join(issues_parts))
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
