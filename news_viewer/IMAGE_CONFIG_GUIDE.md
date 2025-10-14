# 新闻播报图片配置系统

## 功能概述

为新闻播报视频的每个片段配置合适的背景图片，支持：

- ✅ **AI 智能配图**：使用 DeepSeek 分析新闻内容，生成精准的图片搜索关键词
- ✅ **时间轴图片切换**：根据 broadcast.json 的时间轴，为每个片段使用不同的背景
- ✅ **固定图片支持**：intro/outro 可以使用固定图片或留空
- ✅ **目录隔离**：所有图片保存在当天的 broadcast 目录，不污染项目
- ✅ **Unsplash 集成**：从 Unsplash 搜索高质量图片

## 工作流程

```
1. fetch_news.py          - 抓取新闻
2. generate_broadcast.py  - 生成播报稿
3. generate_audio.py      - 生成音频 + 时间轴
4. assign_images.py       - 配置图片 ⭐ 新增
5. add_bgm.py            - 添加背景音乐
6. generate_video_with_timeline.py - 生成视频 ⭐ 新增
```

## 环境配置

### 必需的环境变量

在 `.env` 文件中添加：

```bash
# OpenAI API（用于 DeepSeek）
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com  # 可选
OPENAI_MODEL=deepseek-chat

# Unsplash API（用于图片搜索）
UNSPLASH_ACCESS_KEY=your_access_key_here
```

### 获取 Unsplash API Key

1. 访问 https://unsplash.com/developers
2. 注册账号并创建应用
3. 复制 Access Key 到 `.env`

## 使用方法

### 方法 1：完整工作流（推荐）

```powershell
# 运行完整工作流（包含图片配置）
.\run_workflow.ps1 -UseTimeline

# 跳过某些步骤
.\run_workflow.ps1 -SkipFetch -SkipBroadcast -UseTimeline

# 不使用图片（传统模式）
.\run_workflow.ps1 -SkipImages
```

### 方法 2：单独运行图片配置

```powershell
# 为最新的 broadcast 配置图片
uv run python assign_images.py

# 为指定目录配置图片
uv run python assign_images.py broadcasts/20251014_081240
```

### 方法 3：单独生成时间轴视频

```powershell
# 为最新的 broadcast 生成视频
uv run python generate_video_with_timeline.py

# 为指定目录生成视频
uv run python generate_video_with_timeline.py broadcasts/20251014_081240
```

## 文件结构

```
news_viewer/
├── assign_images.py              # 图片配置工具 ⭐
├── generate_video_with_timeline.py  # 时间轴视频生成器 ⭐
├── intro_background.jpg          # 开场白固定图片（可选）
└── broadcasts/
    └── 20251014_081240/
        ├── broadcast.json        # 包含时间轴和图片路径
        ├── broadcast_full.mp3    # 完整音频
        ├── image_01_world.jpg    # 世界新闻图片 ⭐
        ├── image_02_asia.jpg     # 亚太新闻图片 ⭐
        ├── image_03_americas.jpg # 美洲新闻图片 ⭐
        └── video_full_timeline.mp4  # 最终视频 ⭐
```

## broadcast.json 结构

配置图片后，每个 script 会新增 `image_file` 字段：

```json
{
  "scripts": [
    {
      "category_id": "intro",
      "category_name": "🎙️ 开场白",
      "script": "欢迎收听...",
      "start_time": 0.0,
      "end_time": 4.11,
      "image_file": "intro_background.jpg"  // ⭐ 固定图片
    },
    {
      "category_id": "world",
      "category_name": "🌍 世界新闻",
      "script": "乌克兰无人机...",
      "start_time": 4.11,
      "end_time": 39.8,
      "image_file": "image_01_world.jpg"  // ⭐ AI 配置的图片
    },
    {
      "category_id": "outro",
      "category_name": "🎙️ 结束语",
      "script": "感谢收听...",
      "start_time": 360.38,
      "end_time": 364.68,
      "image_file": null  // ⭐ 不使用图片
    }
  ]
}
```

## 配置说明

### assign_images.py

```python
# 固定图片配置
INTRO_IMAGE = "intro_background.jpg"  # 开场白图片
OUTRO_IMAGE = None  # 结束语图片（None = 不使用）
```

### AI 生成的搜索关键词示例

| 类别 | 播报内容 | AI 生成的关键词 |
|------|---------|----------------|
| 世界新闻 | 乌克兰冲突、中东和平... | `world news global map` |
| 科技新闻 | OpenAI 与博通合作... | `technology digital innovation` |
| 经济新闻 | 美国失业率飙升... | `business finance cityscape` |

### 默认关键词（降级方案）

如果 AI 生成失败，会使用预设的默认关键词：

```python
defaults = {
    "世界": "world news international",
    "亚太": "asia pacific cityscape",
    "美洲": "americas landscape",
    "美国": "united states capitol",
    "中东": "middle east architecture",
    "经济": "economy business finance",
    "科技": "technology digital innovation",
    "科学": "science laboratory research"
}
```

## 技术细节

### 时间轴视频生成原理

1. **按时间轴切分**：根据 broadcast.json 的 start_time/end_time 切分音频
2. **逐片段生成**：为每个片段生成临时视频（音频 + 图片 + 特效）
3. **无缝拼接**：使用 ffmpeg concat 将所有片段拼接成完整视频

### 视觉效果

支持多种音频可视化效果：

- `wave`：波形图（默认，适合新闻播报）
- `vectorscope`：立体声相位图（适合音乐）
- `spectrum`：频谱图
- `none`：仅静态图片

### ffmpeg 命令示例

```bash
# 单个片段（带图片背景）
ffmpeg -ss 4.11 -t 35.7 -i audio.mp3 \
       -loop 1 -i image_01_world.jpg \
       -filter_complex "[1:v]scale=1280:720[bg];
                        [0:a]showwaves=s=1280x200:colors=white[viz];
                        [bg][viz]overlay=0:H-h[out]" \
       -map "[out]" -map "0:a" \
       -c:v libx264 -crf 23 \
       segment_01.mp4

# 拼接所有片段
ffmpeg -f concat -safe 0 -i concat_list.txt \
       -c copy video_full_timeline.mp4
```

## 故障排除

### 问题 1：图片搜索失败

**原因**：Unsplash API 未配置或达到速率限制

**解决方案**：
```bash
# 检查环境变量
echo $env:UNSPLASH_ACCESS_KEY

# 使用默认纯色背景（跳过图片配置）
.\run_workflow.ps1 -SkipImages
```

### 问题 2：AI 关键词生成失败

**原因**：DeepSeek API 配置错误或网络问题

**解决方案**：系统会自动降级到预设的默认关键词

### 问题 3：视频拼接失败

**原因**：ffmpeg concat 对编码格式敏感

**解决方案**：
```powershell
# 检查 ffmpeg 版本
ffmpeg -version

# 手动清理临时文件
Remove-Item broadcasts/*/temp_video_*.mp4
```

## 性能优化

- **并行图片下载**：可以改进为异步下载
- **缓存机制**：相同关键词可以复用图片
- **视频编码**：调整 `-crf` 参数平衡质量和文件大小

## 未来扩展

- [ ] 支持本地图片库
- [ ] 支持视频片段作为背景
- [ ] 添加文字字幕叠加
- [ ] 支持转场效果
- [ ] 图片缓存和复用机制

## 参考资料

- [Unsplash API 文档](https://unsplash.com/documentation)
- [ffmpeg 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html)
- [音频可视化示例](https://trac.ffmpeg.org/wiki/Waveform)
