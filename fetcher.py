"""
RSS 抓取模块 — 从精选源获取最新文章并去重
"""
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser

from config import FETCH_HOURS, MAX_ARTICLES, REQUEST_TIMEOUT, HISTORY_FILE
from sources import SOURCES

logger = logging.getLogger(__name__)


def _parse_published(entry):
    """解析文章的发布时间，返回 datetime 对象"""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _fetch_single_feed(source):
    """抓取单个 RSS 源，返回 (source_info, entries) 或 None"""
    name = source["name"]
    url = source["url"]
    try:
        feed = feedparser.parse(url, request_headers={"User-Agent": "AI-Daily-Bot/1.0"})
        if feed.bozo and not feed.entries:
            logger.warning(f"[{name}] RSS 解析失败: {feed.bozo_exception}")
            return None

        entries = []
        for entry in feed.entries:
            entries.append({
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "published": _parse_published(entry),
                "source_name": name,
                "source_category": source["category"],
                "source_priority": source["priority"],
            })

        logger.info(f"[{name}] 获取到 {len(entries)} 篇文章")
        return entries

    except Exception as e:
        logger.error(f"[{name}] 抓取失败: {e}")
        return None


def fetch_all_feeds():
    """并行抓取所有 RSS 源，返回文章列表"""
    all_entries = []

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(_fetch_single_feed, src): src
            for src in SOURCES
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_entries.extend(result)

    logger.info(f"总共获取 {len(all_entries)} 篇文章")
    return all_entries


def filter_recent(entries, hours=None):
    """过滤最近 N 小时的文章"""
    if hours is None:
        hours = FETCH_HOURS

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    no_date = []

    for entry in entries:
        pub = entry.get("published")
        if pub and pub >= cutoff:
            recent.append(entry)
        elif pub is None:
            # 没有日期的文章也保留，可能是新的
            no_date.append(entry)

    # 有日期的按时间排序，没有日期的追加在后面
    recent.sort(key=lambda e: e["published"], reverse=True)
    result = recent + no_date

    logger.info(f"过滤后剩余 {len(result)} 篇 (最近 {hours}h 内)")
    return result


def _load_history():
    """加载已推送文章的 URL 历史"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("pushed_urls", []))
        except Exception:
            return set()
    return set()


def save_history(urls):
    """保存已推送文章的 URL 列表"""
    # 只保留最近 500 条，防止文件过大
    recent_urls = list(urls)[-500:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "pushed_urls": recent_urls,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }, f, ensure_ascii=False, indent=2)


def deduplicate(entries):
    """基于 URL 去重，排除已推送过的文章"""
    history = _load_history()
    seen = set()
    unique = []

    for entry in entries:
        url = entry.get("link", "")
        if url and url not in history and url not in seen:
            seen.add(url)
            unique.append(entry)

    logger.info(f"去重后剩余 {len(unique)} 篇 (已排除 {len(entries) - len(unique)} 篇)")
    return unique


def prioritize_and_limit(entries, max_count=None):
    """按优先级排序并限制数量"""
    if max_count is None:
        max_count = MAX_ARTICLES

    # 按 priority 升序 (1最高), 同优先级按时间降序
    entries.sort(key=lambda e: (
        e.get("source_priority", 99),
        -(e["published"].timestamp() if e.get("published") else 0)
    ))

    return entries[:max_count]
