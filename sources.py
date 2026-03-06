"""
精选 AI 信息源 — 基于 Zara Zhang「Follow Builders, Not Influencers」理念

分类:
  - company:    AI 公司官方博客 (研究/产品深度文章)
  - builder:    一线 Builder 的个人博客/Newsletter
  - podcast:    高质量 AI 播客
  - newsletter: 行业深度 Newsletter

每个源包含: name, url, category, priority (1=最高, 3=最低)
"""

SOURCES = [
    # ===== AI 公司官方 =====
    {
        "name": "OpenAI",
        "url": "https://openai.com/news/rss.xml",
        "category": "company",
        "priority": 1,
    },
    {
        "name": "Anthropic",
        "url": "https://www.anthropic.com/research/rss.xml",
        "category": "company",
        "priority": 1,
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml",
        "category": "company",
        "priority": 1,
    },
    {
        "name": "Meta Research",
        "url": "https://research.facebook.com/feed/",
        "category": "company",
        "priority": 1,
    },
    {
        "name": "Hugging Face",
        "url": "https://huggingface.co/blog/feed.xml",
        "category": "company",
        "priority": 2,
    },
    {
        "name": "Microsoft Research",
        "url": "https://www.microsoft.com/en-us/research/feed/",
        "category": "company",
        "priority": 2,
    },
    {
        "name": "NVIDIA AI",
        "url": "https://blogs.nvidia.com/feed/",
        "category": "company",
        "priority": 2,
    },

    # ===== Builder 个人博客/Newsletter =====
    # Zara Zhang 推荐 + 一线 AI 践行者
    {
        "name": "Andrej Karpathy",
        "url": "https://karpathy.bearblog.dev/feed/",
        "category": "builder",
        "priority": 1,
    },
    {
        "name": "Zara Zhang",
        "url": "https://zarazhang.substack.com/feed",
        "category": "builder",
        "priority": 1,
    },
    {
        "name": "Lilian Weng (OpenAI)",
        "url": "https://lilianweng.github.io/index.xml",
        "category": "builder",
        "priority": 1,
    },
    {
        "name": "Simon Willison",
        "url": "https://simonwillison.net/atom/everything/",
        "category": "builder",
        "priority": 1,
    },
    {
        "name": "Swyx (Latent Space)",
        "url": "https://latent.space/feed",
        "category": "builder",
        "priority": 1,
    },

    # ===== 高质量 AI 播客 (Zara 推荐) =====
    {
        "name": "Latent Space Podcast",
        "url": "https://rss.flightcast.com/vgnxzgiwwzwke85ym53fjnzu.xml",
        "category": "podcast",
        "priority": 1,
    },
    {
        "name": "No Priors",
        "url": "https://rss.art19.com/no-priors-ai",
        "category": "podcast",
        "priority": 1,
    },
    {
        "name": "Dwarkesh Podcast",
        "url": "https://apple.dwarkesh-podcast.workers.dev/feed.rss",
        "category": "podcast",
        "priority": 2,
    },

    # ===== 行业 Newsletter =====
    {
        "name": "Import AI (Jack Clark)",
        "url": "https://importai.substack.com/feed",
        "category": "newsletter",
        "priority": 2,
    },
]

# 分类显示名称和 Emoji
CATEGORY_LABELS = {
    "company":    "🏢 公司深度",
    "builder":    "🛠️ Builder 视角",
    "podcast":    "🎙️ 播客精选",
    "newsletter": "📰 行业洞察",
}

# 分类显示顺序 — Builder 内容优先
CATEGORY_ORDER = ["builder", "company", "podcast", "newsletter"]
