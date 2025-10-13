# 新闻播报系统使用指南

## 📁 目录结构

```
news_viewer/
├── broadcasts/              # 播报文件主目录
│   ├── 20251014_003016/    # 以时间戳命名的子目录
│   │   ├── broadcast.json  # 播报稿 JSON
│   │   ├── broadcast.txt   # 播报稿文本
│   │   ├── broadcast_00_intro.mp3       # 开场白
│   │   ├── broadcast_01_world.mp3       # 世界新闻
│   │   ├── broadcast_02_asia.mp3        # 亚太新闻
│   │   ├── ...
│   │   └── broadcast_full.mp3           # 完整音频
│   └── 20251014_120000/    # 另一个时间段的播报
│       └── ...
├── generate_broadcast.py   # 生成播报稿脚本
└── generate_audio.py       # 生成音频脚本
```

## 🚀 使用流程

### 1. 生成播报稿

```powershell
# 读取 news.json，生成播报稿
uv run python generate_broadcast.py

# 会在 broadcasts/ 下创建时间戳子目录，如：
# broadcasts/20251014_120000/
#   ├── broadcast.json
#   └── broadcast.txt
```

### 2. 生成音频

```powershell
# 方式1：自动使用最新的播报目录
uv run python generate_audio.py

# 方式2：指定子目录名称
uv run python generate_audio.py 20251014_120000

# 方式3：指定完整路径
uv run python generate_audio.py broadcasts/20251014_120000/broadcast.json
```

音频文件会保存在对应的子目录中。

## 🎯 优势

### 组织清晰
- ✅ 每次播报都有独立的子目录
- ✅ 所有相关文件（JSON、TXT、MP3）都在一个目录中
- ✅ 通过时间戳命名，易于查找和管理

### 自动化
- ✅ 默认使用最新的播报目录
- ✅ 支持灵活的路径指定方式
- ✅ 自动查找目录中的 JSON 文件

### 易于维护
- ✅ 可以整体删除某个播报
- ✅ 可以方便地备份或分享某个播报
- ✅ broadcasts 主目录不会混乱

## 📝 环境变量

需要在 `.env` 文件中配置：

```bash
# 火山引擎 TTS
VOLCENGINE_APP_ID=your-app-id
VOLCENGINE_ACCESS_TOKEN=your-access-token

# OpenAI API（用于生成播报稿）
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
OPENAI_MODEL=gpt-4o-mini  # 可选
```

## 🔧 高级用法

### 转换已有的 WAV 文件

```powershell
uv run python generate_audio.py --convert path/to/audio.wav
```

### 批量处理

```powershell
# 生成多个播报
foreach ($i in 1..3) {
    uv run python generate_broadcast.py
    Start-Sleep -Seconds 2
}

# 为所有播报生成音频
Get-ChildItem broadcasts -Directory | ForEach-Object {
    uv run python generate_audio.py $_.Name
}
```

## 🎤 音频质量

- **格式**: MP3
- **采样率**: 24000 Hz
- **比特率**: 128 kbps
- **声音**: 知性温婉女声 (ICL_zh_female_zhixingwenwan_tob)
- **引擎**: 火山引擎 TTS API

## 📦 示例输出

```
broadcasts/
└── 20251014_120000/
    ├── broadcast.json              (播报稿数据)
    ├── broadcast.txt               (纯文本版)
    ├── broadcast_00_intro.mp3      (90.5 KB, 3.6秒)
    ├── broadcast_01_world.mp3      (801.6 KB, 42秒)
    ├── broadcast_02_asia.mp3       (749.1 KB, 39秒)
    ├── broadcast_03_americas.mp3   (798.3 KB, 40秒)
    ├── broadcast_04_us.mp3         (717.2 KB, 37秒)
    ├── broadcast_05_middleeast.mp3 (846.1 KB, 43秒)
    ├── broadcast_06_economy.mp3    (987.7 KB, 49秒)
    ├── broadcast_07_technology.mp3 (871.4 KB, 42秒)
    ├── broadcast_08_science.mp3    (896.2 KB, 46秒)
    ├── broadcast_09_outro.mp3      (86.7 KB, 3.5秒)
    └── broadcast_full.mp3          (6845.2 KB, 完整版)
```

## 🎧 播放音频

```powershell
# 播放完整版
Start-Process broadcasts/20251014_120000/broadcast_full.mp3

# 或使用 Windows Media Player
& "C:\Program Files\Windows Media Player\wmplayer.exe" broadcasts/20251014_120000/broadcast_full.mp3
```
