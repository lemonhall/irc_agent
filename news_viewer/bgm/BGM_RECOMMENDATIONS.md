# 新闻播报 BGM 推荐

## 🎵 推荐曲目（免版权/CC协议）

### 1. 新闻主题风格

#### **推荐：Corporate Business Background Music**
- 风格：专业、平稳、不抢戏
- 来源：YouTube Audio Library
- 搜索关键词：`corporate background music`
- 时长：通常 3-10 分钟

#### **推荐：Soft Piano - Peaceful**
- 风格：轻柔钢琴，适合清晨播报
- 来源：Pixabay Music
- 搜索关键词：`peaceful piano background`
- 时长：通常 2-8 分钟

#### **推荐：Ambient News Theme**
- 风格：环境音乐，现代感
- 来源：Free Music Archive
- 搜索关键词：`ambient news background`
- 时长：通常 5-15 分钟

### 2. 具体推荐（可直接搜索）

| 曲名 | 艺术家 | 风格 | 来源 |
|------|--------|------|------|
| "Inspiring Corporate" | Rafael Krux | 商务 | YouTube Audio Library |
| "Calm Piano" | Luke Bergs | 钢琴 | Pixabay |
| "News Theme" | Kevin MacLeod | 新闻 | Incompetech |
| "Meditation Impromptu" | Kevin MacLeod | 平静 | Incompetech |
| "Acoustic Breeze" | Benjamin Tissot | 吉他 | Bensound |

## 📥 快速下载指南

### YouTube Audio Library（推荐）
1. 访问：https://studio.youtube.com/channel/UCxxxxxxx/music
2. 需要 Google 账号登录
3. 筛选条件：
   - Genre: Ambient / Electronic / Classical
   - Mood: Calm / Happy / Bright
   - Duration: 5-10 minutes
4. 下载后放入 `bgm/` 目录

### Pixabay Music（最简单）
1. 访问：https://pixabay.com/music/
2. 搜索：`piano background` 或 `corporate music`
3. 筛选 5 分钟以上
4. 直接下载 MP3

### Incompetech（经典）
1. 访问：https://incompetech.com/music/royalty-free/music.html
2. Browse by Genre → Cinematic / Corporate
3. 试听后下载（需标注作者）
4. License: CC BY 4.0

## 🎹 音乐特征建议

适合新闻播报的 BGM 特征：

✅ **应该有的特征：**
- 节奏平稳，120 BPM 以下
- 没有明显的人声或歌词
- 音量动态范围小（不要有突然的高低音）
- 循环性好（首尾衔接自然）
- 长度 5 分钟以上

❌ **应该避免：**
- 节奏强烈的鼓点
- 有人声或歌词
- 情绪起伏太大
- 过于欢快或过于悲伤
- 太短（少于 3 分钟会频繁循环）

## 🔧 使用方法

```powershell
# 1. 下载 BGM 后放入 bgm 目录
# 2. 运行混音脚本
cd news_viewer
uv run python add_bgm.py

# 3. 如果觉得音乐太响或太轻，调整音量
uv run python add_bgm.py --volume 0.1  # 更轻
uv run python add_bgm.py --volume 0.2  # 更响
```

## 🎧 我的个人推荐

基于新闻播报场景，我最推荐：

1. **Kevin MacLeod - "Meditation Impromptu 03"**
   - 理由：轻柔钢琴，循环性好，不抢戏
   - 下载：https://incompetech.com/music/royalty-free/

2. **"Soft Piano Background Music"** (Pixabay)
   - 理由：专为背景设计，音量平稳
   - 搜索：Pixabay → "soft piano 5 minutes"

3. **"Corporate Technology"** (YouTube Audio Library)
   - 理由：现代感，适合科技新闻
   - 位置：YouTube Studio → Audio Library → Genre: Electronic

## 📝 版权说明

使用免费音乐时注意：

- ✅ CC0 / Public Domain - 完全免费，无需标注
- ✅ CC BY - 免费，需要标注作者
- ⚠️ YouTube Audio Library - 免费，但仅限 YouTube 使用（部分曲目）
- ⚠️ Epidemic Sound - 需要订阅

建议使用 **CC0** 或 **CC BY** 协议的音乐。

## 🆘 找不到合适的？

如果实在找不到合适的 BGM，可以考虑：

1. **不加 BGM** - 纯人声也很专业
2. **环境白噪音** - 轻微的咖啡厅环境音
3. **自己生成** - 使用 AI 音乐生成工具（如 Suno AI）

## 🎼 AI 生成 BGM（实验性）

可以尝试用 AI 生成定制 BGM：

- **Suno AI**: https://suno.ai/
  - Prompt: "soft ambient piano background music for news broadcast, calm, 5 minutes, no vocals"
  
- **Udio**: https://udio.com/
  - Prompt: "corporate background music, peaceful, instrumental only"

生成后下载，放入 `bgm/` 目录即可使用。
