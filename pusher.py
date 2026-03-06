"""
Server酱推送模块 — 将消息推送到微信
"""
import logging

import requests

from config import SERVERCHAN_SENDKEY, SERVERCHAN_API_URL

logger = logging.getLogger(__name__)


def push_to_wechat(title, body):
    """
    通过 Server酱将消息推送到微信

    Args:
        title: 消息标题 (≤256字符)
        body: 消息正文 (支持 Markdown, ≤64KB)

    Returns:
        True 表示发送成功, False 表示失败
    """
    if not SERVERCHAN_SENDKEY:
        logger.error("SERVERCHAN_SENDKEY 未设置！请在 .env 文件中配置。")
        return False

    # 截断标题
    if len(title) > 256:
        title = title[:253] + "..."

    # 截断正文
    max_body_bytes = 60 * 1024  # 留一些余量，不用满 64KB
    if len(body.encode("utf-8")) > max_body_bytes:
        body = body[:max_body_bytes // 4]  # 粗略截断
        body += "\n\n...(内容过长已截断)"

    url = SERVERCHAN_API_URL.format(key=SERVERCHAN_SENDKEY)

    try:
        resp = requests.post(url, data={
            "title": title,
            "desp": body,
        }, timeout=10)

        result = resp.json()

        if result.get("code") == 0:
            logger.info(f"✅ 推送成功: {title}")
            return True
        else:
            logger.error(f"❌ 推送失败: {result.get('message', '未知错误')}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 推送请求失败: {e}")
        return False


def test_push():
    """发送一条测试消息验证通道是否正常"""
    from formatter import format_test_message
    title, body = format_test_message()
    return push_to_wechat(title, body)
