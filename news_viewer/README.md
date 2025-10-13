# 📰 新闻阅读器

一个简单优雅的新闻阅读工具，从纽约时报 RSS 获取全球和亚太新闻，使用 AI 翻译标题。

## ✨ 特点

- 📡 实时抓取纽约时报全球和亚太新闻
- 🌐 AI 智能翻译英文标题为中文
- 💾 输出 JSON 格式数据
- 🎨 漂亮的网页界面展示
- 🔄 支持自动刷新

## 🚀 使用方法

### 方法 1: 一键启动（推荐）

**Windows 用户**：
```powershell
# 双击运行
启动新闻阅读器.ps1

# 或在 PowerShell 中运行
.\启动新闻阅读器.ps1
```

**或使用 Python**：
```bash
cd news_viewer
uv run python run.py
```

这会自动：
1. ✅ 抓取最新新闻并翻译
2. ✅ 启动本地服务器
3. ✅ 自动打开浏览器

### 方法 2: 分步操作

#### 步骤 1: 抓取新闻

```bash
# 进入 news_viewer 目录
cd news_viewer

# 获取默认 5 条新闻
uv run python fetch_news.py

# 自定义数量（比如 10 条）
uv run python fetch_news.py 10
```

#### 步骤 2: 启动服务器

```bash
# 启动 HTTP 服务器
uv run python start_server.py

# 然后访问 http://localhost:8000
```

## 📁 文件说明

```
news_viewer/
├── fetch_news.py          # 新闻抓取脚本（含翻译）
├── start_server.py        # HTTP 服务器
├── run.py                 # 一键启动脚本
├── 启动新闻阅读器.ps1      # Windows 启动脚本
├── news.json              # 生成的新闻数据
├── index.html             # 网页展示界面
└── README.md              # 本说明文件
```

## 🛠️ 技术栈

- **数据获取**: httpx + RSS
- **AI 翻译**: DeepSeek API
- **前端**: 纯 HTML + CSS + JavaScript
- **数据格式**: JSON

## 📝 生成的 JSON 格式

```json
{
  "update_time": "2025-10-13 23:45:00",
  "categories": [
    {
      "id": "world",
      "name": "🌍 世界新闻",
      "news": [
        {
          "title": "英文标题",
          "title_cn": "中文翻译",
          "link": "https://...",
          "pubdate": "..."
        }
      ]
    }
  ]
}
```

## ⚙️ 配置

需要在项目根目录的 `.env` 文件中配置 DeepSeek API：

```bash
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

## 🎯 自动化

### 定时抓取（可选）

**Windows 任务计划程序**：
- 每天早上 8 点运行 `fetch_news.py`

**Linux/Mac Cron**：
```bash
0 8 * * * cd /path/to/news_viewer && python fetch_news.py
```

## 🌈 效果预览

- 渐变紫色背景
- 卡片式新闻布局
- 中英文双语显示
- 悬停动画效果
- 响应式设计（支持手机）

## 📄 许可

MIT License
