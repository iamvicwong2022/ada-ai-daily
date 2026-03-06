"""
Ada AI 日报 — 主程序

用法:
  python main.py              # 正常运行: 抓取 → 摘要 → 推送
  python main.py --test       # 测试模式: 只抓取和摘要, 不推送
  python main.py --test-push  # 测试推送: 发送一条测试消息到微信
  python main.py --hours 48   # 自定义时间窗口 (默认24小时)
  python main.py --no-summary # 跳过AI摘要 (快速测试抓取)
"""
import argparse
import logging
import sys

from fetcher import fetch_all_feeds, filter_recent, deduplicate, prioritize_and_limit, save_history
from summarizer import process_articles
from formatter import format_daily_digest
from html_generator import generate_html_digest
from pusher import push_to_wechat, test_push
from config import GITHUB_PAGES_URL


def setup_logging():
    """配置日志输出"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(description="Ada AI 日报")
    parser.add_argument("--test", action="store_true",
                        help="测试模式: 抓取和摘要, 但不推送")
    parser.add_argument("--test-push", action="store_true",
                        help="发送一条测试消息到微信")
    parser.add_argument("--hours", type=int, default=None,
                        help="自定义时间窗口 (小时, 默认24)")
    parser.add_argument("--no-summary", action="store_true",
                        help="跳过AI摘要 (快速测试抓取)")
    parser.add_argument("--no-html", action="store_true",
                        help="不生成 HTML 页面")

    args = parser.parse_args()
    setup_logging()
    logger = logging.getLogger(__name__)

    # === 测试推送模式 ===
    if args.test_push:
        logger.info("📤 发送测试消息...")
        success = test_push()
        if success:
            logger.info("✅ 测试消息已发送，请查看微信！")
        else:
            logger.error("❌ 测试消息发送失败，请检查 SERVERCHAN_SENDKEY")
        return

    # === 正常流程 ===
    logger.info("=" * 50)
    logger.info("🚀 Ada AI 日报启动")
    logger.info("=" * 50)

    # Step 1: 抓取 RSS
    logger.info("\n📡 Step 1/5: 抓取 RSS 源...")
    all_entries = fetch_all_feeds()
    if not all_entries:
        logger.warning("⚠️ 未获取到任何文章，退出")
        return

    # Step 2: 过滤最近文章
    logger.info("\n🕐 Step 2/5: 过滤最近文章...")
    recent = filter_recent(all_entries, hours=args.hours)

    # Step 3: 去重
    logger.info("\n🔍 Step 3/5: URL 去重...")
    unique = deduplicate(recent)
    if not unique:
        logger.info("📭 没有新文章，今日无需推送")
        return

    # 优先级排序 + 数量限制
    articles = prioritize_and_limit(unique)
    logger.info(f"📋 最终选取 {len(articles)} 篇文章")

    # 记录过滤数量
    pre_filter_count = len(articles)

    # Step 4: Ada 评估 + 点评
    if not args.no_summary:
        logger.info("\n🧠 Step 4/5: Ada 评估内容价值 + 生成点评...")
        articles = process_articles(articles)
    else:
        logger.info("\n⏭️ Step 4/5: 跳过 Ada 评估")
        for a in articles:
            a["chinese_summary"] = ""
            a["ada_comment"] = ""

    # Step 5: 生成内容
    logger.info("\n📝 Step 5/6: 生成简报...")
    title, body = format_daily_digest(articles)

    # Step 6: 生成 HTML + 推送
    filtered_count = pre_filter_count - len(articles)
    html_url = None

    if not args.no_html:
        logger.info("\n🌐 Step 6/6: 生成 HTML 日报...")
        filename, html_content, url_path = generate_html_digest(
            articles, filtered_count=filtered_count
        )
        logger.info(f"✅ HTML 已保存: docs/{filename}")

        if GITHUB_PAGES_URL:
            html_url = f"{GITHUB_PAGES_URL.rstrip('/')}/{filename}"
            logger.info(f"🔗 在线链接: {html_url}")

    # 打印简报预览
    logger.info(f"\n{'='*50}")
    logger.info(f"简报标题: {title}")
    logger.info(f"{'='*50}")
    print(body[:1000])
    if len(body) > 1000:
        print(f"\n... (共 {len(body)} 字符)")

    if args.test:
        logger.info("\n🧪 测试模式 — 不推送")
    else:
        # 推送到微信 (如果有 HTML 链接则推送带链接的通知)
        if html_url:
            notify_title = title
            notify_body = (
                f"> *Follow Builders, Not Influencers*\n\n"
                f"今日精选 **{len(articles)}** 篇, 过滤 {filtered_count} 篇\n\n"
                f"👉 [点击阅读完整日报]({html_url})\n\n"
                f"---\n\n"
                + body
            )
            success = push_to_wechat(notify_title, notify_body)
        else:
            success = push_to_wechat(title, body)

        if success:
            pushed_urls = {a["link"] for a in articles if a.get("link")}
            save_history(pushed_urls)
            logger.info("✅ 推送完成！请查看微信。")
        else:
            logger.error("❌ 推送失败！")
            sys.exit(1)


if __name__ == "__main__":
    main()
