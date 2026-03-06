"""
配置模块 — 加载环境变量和全局参数
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(Path(__file__).parent / ".env")

# === API Keys ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SERVERCHAN_SENDKEY = os.getenv("SERVERCHAN_SENDKEY", "")

# === 抓取参数 ===
FETCH_HOURS = 24              # 抓取最近 N 小时的文章
MAX_ARTICLES = 15             # 每日简报最大条目数
REQUEST_TIMEOUT = 15          # RSS 请求超时（秒）

# === AI 摘要参数 ===
GEMINI_MODEL = "gemini-2.5-flash-lite"  # 免费额度充足, 理解力足够
SUMMARY_MAX_TOKENS = 500      # 摘要 + Ada 点评需要更多 token

# === Server酱参数 ===
SERVERCHAN_API_URL = "https://sctapi.ftqq.com/{key}.send"

# === 文件路径 ===
PROJECT_DIR = Path(__file__).parent
HISTORY_FILE = PROJECT_DIR / "history.json"

# === GitHub Pages ===
# 部署后填入你的 GitHub Pages URL, 例如: https://username.github.io/ada-ai-daily
GITHUB_PAGES_URL = os.getenv("GITHUB_PAGES_URL", "")
