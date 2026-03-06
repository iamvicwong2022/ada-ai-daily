# 🤖 AI 每日资讯聚合器

自动从精选一手 AI 信息源抓取最新内容，通过 Gemini API 生成中文摘要，推送到微信。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Keys

复制环境变量模板并填入你的 Key：

```bash
copy .env.example .env
```

编辑 `.env` 文件：
```
GEMINI_API_KEY=你的_Gemini_API_Key
SERVERCHAN_SENDKEY=你的_Server酱_SendKey
```

**获取方式：**
- Gemini API Key: [aistudio.google.com](https://aistudio.google.com) → 获取 API Key
- Server酱 SendKey: [sct.ftqq.com](https://sct.ftqq.com) → 微信扫码登录 → 复制 SendKey

### 3. 测试推送

```bash
python main.py --test-push
```

如果微信收到测试消息，说明配置成功！

### 4. 运行

```bash
# 正常运行 (抓取 + 摘要 + 推送)
python main.py

# 测试模式 (不推送, 只查看简报内容)
python main.py --test

# 快速测试 (跳过AI摘要)
python main.py --test --no-summary

# 自定义时间窗口
python main.py --hours 48
```

## ⏰ 设置每日定时运行

### Windows 任务计划程序

1. 打开 **任务计划程序** (`taskschd.msc`)
2. 点击 **创建基本任务**
3. 名称: `AI Daily Digest`
4. 触发器: **每天** → 设定时间 (建议早上 8:00)
5. 操作: **启动程序**
   - 程序: `python`
   - 参数: `main.py`
   - 起始位置: `C:\Users\user\antigravity_project\AI Info Collection`
6. 完成

## 📰 信息源

| 来源 | 类别 |
|------|------|
| OpenAI Blog | 公司动态 |
| Anthropic News | 公司动态 |
| Google DeepMind | 公司动态 |
| Meta AI Blog | 公司动态 |
| xAI (Grok) | 公司动态 |
| Hugging Face Blog | 公司动态 |
| Andrej Karpathy | 人物观点 |
| Zara Zhang | 人物观点 |
| Lilian Weng | 人物观点 |
| Import AI | Newsletter |
| The Batch | Newsletter |
| arXiv cs.AI | 学术前沿 |

> 在 `sources.py` 中可随时增减信息源。

## 📂 文件说明

| 文件 | 功能 |
|------|------|
| `main.py` | 主程序入口 |
| `config.py` | 配置参数 |
| `sources.py` | RSS 信息源列表 |
| `fetcher.py` | RSS 抓取 + 去重 |
| `summarizer.py` | Gemini API 中文摘要 |
| `formatter.py` | Markdown 简报生成 |
| `pusher.py` | Server酱微信推送 |
| `history.json` | 已推送记录 (自动生成) |
