# 新闻播报自动化脚本使用说明

## 🚀 快速开始

### Windows (PowerShell)

```powershell
# 完整工作流（全自动）
.\run_workflow.ps1

# 跳过某些步骤
.\run_workflow.ps1 -SkipFetch        # 跳过新闻抓取
.\run_workflow.ps1 -SkipBroadcast    # 跳过播报稿生成
.\run_workflow.ps1 -SkipAudio        # 跳过音频生成
.\run_workflow.ps1 -SkipBGM          # 跳过背景音乐

# 调整 BGM 音量
.\run_workflow.ps1 -BGMVolume 0.2    # 20% 音量
.\run_workflow.ps1 -BGMVolume 0.1    # 10% 音量

# 组合使用（例如：使用已有播报稿，只生成音频）
.\run_workflow.ps1 -SkipFetch -SkipBroadcast
```

### Linux/Debian (Bash)

```bash
# 先添加执行权限
chmod +x run_workflow.sh

# 完整工作流（全自动）
./run_workflow.sh

# 跳过某些步骤
./run_workflow.sh --skip-fetch        # 跳过新闻抓取
./run_workflow.sh --skip-broadcast    # 跳过播报稿生成
./run_workflow.sh --skip-audio        # 跳过音频生成
./run_workflow.sh --skip-bgm          # 跳过背景音乐

# 调整 BGM 音量
./run_workflow.sh --bgm-volume 0.2    # 20% 音量
./run_workflow.sh --bgm-volume 0.1    # 10% 音量

# 组合使用（例如：使用已有播报稿，只生成音频）
./run_workflow.sh --skip-fetch --skip-broadcast

# 查看帮助
./run_workflow.sh --help
```

## 📋 工作流程说明

脚本会自动执行以下 4 个步骤：

### 1️⃣ 抓取新闻 (`fetch_news.py`)
- 从新闻源抓取最新新闻
- 生成 `news.json` 文件

### 2️⃣ 生成播报稿 (`generate_broadcast.py`)
- 读取 `news.json`
- 使用 AI 生成播报稿
- 在 `broadcasts/` 下创建时间戳子目录（如 `20251014_120000/`）
- 生成 `broadcast.json` 和 `broadcast.txt`

### 3️⃣ 生成音频 (`generate_audio.py`)
- 读取 `broadcast.json`
- 使用火山引擎 TTS 生成各个板块的 MP3
- 合并生成完整版：`broadcast_full.mp3`

### 4️⃣ 添加背景音乐 (`add_bgm.py`)
- 读取 `bgm/` 目录中的背景音乐
- 将 BGM 混入 `broadcast_full.mp3`
- 生成最终版本：`broadcast_full_with_bgm.mp3`

## 🎯 常见使用场景

### 场景 1：每日定时生成新闻播报

```powershell
# Windows - 使用任务计划程序
# 创建任务，每天运行：
powershell.exe -File "E:\development\irc_agent\news_viewer\run_workflow.ps1"
```

```bash
# Linux - 使用 crontab
# 每天 8:00 生成新闻播报
0 8 * * * /path/to/irc_agent/news_viewer/run_workflow.sh
```

### 场景 2：快速重新生成音频（不抓取新闻）

```powershell
# Windows
.\run_workflow.ps1 -SkipFetch
```

```bash
# Linux
./run_workflow.sh --skip-fetch
```

### 场景 3：测试不同 BGM 效果

```powershell
# Windows - 先生成无 BGM 版本
.\run_workflow.ps1 -SkipBGM

# 然后手动测试不同音量
python add_bgm.py --volume 0.1
python add_bgm.py --volume 0.15
python add_bgm.py --volume 0.2
```

### 场景 4：只生成播报稿（不生成音频）

```powershell
# Windows
.\run_workflow.ps1 -SkipAudio -SkipBGM
```

```bash
# Linux
./run_workflow.sh --skip-audio --skip-bgm
```

## 📁 输出目录结构

```
broadcasts/
└── 20251014_120000/        # 时间戳命名的子目录
    ├── broadcast.json      # 播报稿数据
    ├── broadcast.txt       # 纯文本版
    ├── broadcast_00_intro.mp3
    ├── broadcast_01_world.mp3
    ├── broadcast_02_asia.mp3
    ├── ...
    ├── broadcast_full.mp3           # 纯人声完整版
    └── broadcast_full_with_bgm.mp3  # 带背景音乐完整版
```

## ⚙️ 前置要求

### 必需的环境变量

在 `.env` 文件中配置：

```bash
# 火山引擎 TTS
VOLCENGINE_APP_ID=your-app-id
VOLCENGINE_ACCESS_TOKEN=your-access-token

# OpenAI API（用于生成播报稿）
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
OPENAI_MODEL=gpt-4o-mini                    # 可选
```

### 必需的软件

- **Python 3.10+**
- **uv** (Python 包管理器)
- **ffmpeg** (音频处理)

安装 ffmpeg：

```bash
# Windows (使用 Chocolatey)
choco install ffmpeg

# Debian/Ubuntu
sudo apt update
sudo apt install ffmpeg

# 验证安装
ffmpeg -version
```

### BGM 准备

在第一次运行前，建议在 `bgm/` 目录中放入背景音乐文件：

```bash
news_viewer/
└── bgm/
    └── background_music.mp3  # 你的背景音乐（建议 5-10 分钟）
```

参考 `bgm/BGM_RECOMMENDATIONS.md` 获取推荐音乐。

## 🐛 故障排除

### 错误：虚拟环境不存在

```bash
# 创建虚拟环境
cd E:\development\irc_agent  # Windows
cd /path/to/irc_agent        # Linux

uv venv
uv pip install -r requirements.txt
```

### 错误：未找到 ffmpeg

确保 ffmpeg 已安装并添加到 PATH：

```bash
# 测试
ffmpeg -version
```

### 错误：API 密钥未设置

检查 `.env` 文件是否存在并包含必要的 API 密钥。

### 警告：BGM 目录为空

将背景音乐文件放入 `news_viewer/bgm/` 目录，或使用 `-SkipBGM` / `--skip-bgm` 跳过。

## 💡 提示

- 首次运行建议逐步执行，确保每个步骤都正常
- 生成的音频文件较大，注意磁盘空间
- 可以定期清理旧的播报目录
- BGM 音量默认 15%，可根据实际效果调整

## 📞 获取帮助

查看各个脚本的详细文档：

- `USAGE_GUIDE.md` - 完整使用指南
- `bgm/BGM_RECOMMENDATIONS.md` - BGM 推荐
- `工作流.md` - 工作流程说明
