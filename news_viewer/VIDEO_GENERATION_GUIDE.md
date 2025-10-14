# 新闻播报视频生成功能说明

## 📹 功能概述

将新闻播报音频（MP3）+ 静态图片合成为视频（MP4），支持多种音频可视化效果。

---

## 🎬 视觉效果类型

### 1. **Wave（波形图）** - 推荐播客/新闻
```
━━━━━━━━━━━━━━━━━━━━━━━━
  传统音频波形，优雅简洁
━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. **Spectrum（频谱图）** - 推荐音乐
```
║║║║║║║║║║║║║║║║║║║║
  频率柱状图，动感炫酷
║║║║║║║║║║║║║║║║║║║║
```

### 3. **Vectorscope（矢量示波器）** - 高端效果
```
    ╱╲
   ╱  ╲
  ╱    ╲
  立体声相位图，圆形波浪
```

### 4. **None（无效果）** - 纯静态图片
```
只有背景图片 + 音频
```

---

## 🚀 快速使用

### 方法 1: 完整工作流（推荐）
```powershell
# 完整流程：抓新闻 → 生成播报 → 生成音频 → 添加BGM → 生成视频
.\run_workflow.ps1

# 跳过某些步骤（如只生成视频）
.\run_workflow.ps1 -SkipFetch -SkipBroadcast -SkipAudio -SkipBGM
```

### 方法 2: 单独生成视频
```powershell
# 快速测试：处理最新播报，生成多种效果
.\生成视频.ps1

# 或直接运行
uv run python generate_video.py
```

### 方法 3: Python API（高级用户）
```python
from pathlib import Path
from generate_video import NewsVideoGenerator

# 初始化生成器
generator = NewsVideoGenerator()

# 生成视频
generator.generate_video(
    audio_path=Path("audio.mp3"),
    output_path=Path("output.mp4"),
    image_path=Path("background.jpg"),  # 可选
    effect="wave",                       # wave/spectrum/vectorscope/none
    wave_position="bottom",              # top/bottom/center
    color_scheme="tech",                 # default/gradient/blue/gold/tech
    wave_height=200,                     # 波形高度（像素）
    video_quality=23                     # 18=高质量，28=低质量
)
```

---

## 🎨 颜色方案

| 方案 | 效果 | 适用场景 |
|------|------|---------|
| `default` | 纯白色 | 简洁专业 |
| `gradient` | 红绿蓝渐变 | 彩虹效果 |
| `blue` | 天蓝色 | 科技冷色 |
| `gold` | 金色 | 高端商务 |
| `tech` | 青绿渐变 | 科技未来感 ⭐ |

---

## 🖼️ 背景图片管理

### 下载背景图片
```powershell
uv run python download_background.py
```

支持的主题：
1. 新闻演播室
2. 现代办公室
3. 科技抽象
4. 纯色渐变（本地生成，无需网络）

### 使用自定义图片
1. 将图片命名为 `news_background.jpg`
2. 放在 `news_viewer/` 目录
3. 推荐尺寸：1280x720（16:9）

### 无背景图片时
系统会自动使用深蓝色纯色背景。

---

## 📊 输出示例

```
broadcasts/
└── 20251014_081240/
    ├── broadcast.json
    ├── broadcast.txt
    ├── audio_full.mp3              # 原始音频
    ├── audio_full_with_bgm.mp3     # 带BGM音频
    ├── video_full_with_bgm.mp4     # 波形视频（科技风）
    └── video_full_with_bgm_1.mp4   # 频谱视频（渐变）
```

---

## 🔧 技术参数说明

### 视频质量（CRF）
- `18`: 高质量，文件大（约 5-10 MB/分钟）
- `23`: 平衡质量（推荐，约 2-5 MB/分钟）⭐
- `28`: 低质量，文件小（约 1-2 MB/分钟）

### 波形高度
- `100`: 细线效果
- `200`: 标准高度 ⭐
- `300`: 粗壮醒目

### 波形位置
- `bottom`: 底部（推荐）⭐
- `top`: 顶部
- `center`: 居中（仅 vectorscope 推荐）

---

## 🎯 常见用例

### 播客/新闻播报（推荐配置）
```python
generator.generate_video(
    audio_path=audio,
    output_path=output,
    effect="wave",
    color_scheme="tech",
    wave_position="bottom",
    video_quality=23
)
```

### 音乐可视化
```python
generator.generate_video(
    audio_path=audio,
    output_path=output,
    effect="spectrum",
    color_scheme="gradient",
    wave_position="bottom",
    video_quality=20  # 音乐需要更高质量
)
```

### 极简风格
```python
generator.generate_video(
    audio_path=audio,
    output_path=output,
    effect="none",  # 无可视化
    video_quality=25  # 静态图片可以降低质量
)
```

---

## 📦 依赖要求

### 必需
- **ffmpeg**: 音视频处理核心工具
  - Windows: 下载 https://ffmpeg.org/download.html
  - 解压后将 `bin/` 目录添加到 PATH

### 可选
- **Pillow**: 用于本地生成渐变背景
  ```bash
  uv pip install Pillow
  ```

### 检查依赖
```powershell
# 检查 ffmpeg
ffmpeg -version

# 测试视频生成
.\生成视频.ps1
```

---

## 🐛 故障排除

### ❌ "ffmpeg 不可用"
**原因**: ffmpeg 未安装或不在 PATH 中
**解决**: 
1. 下载 ffmpeg: https://ffmpeg.org/download.html
2. 解压到 `C:\ffmpeg`
3. 添加 `C:\ffmpeg\bin` 到系统 PATH
4. 重启终端验证: `ffmpeg -version`

### ❌ "背景图片不存在"
**原因**: 未准备背景图片
**解决**:
```powershell
# 选项1: 下载图片
uv run python download_background.py

# 选项2: 使用纯色背景（自动降级）
# 系统会自动使用深蓝色背景，无需手动操作
```

### ❌ 视频文件过大
**原因**: CRF 值设置过低
**解决**: 提高 `video_quality` 参数（如 23 → 26）

### ❌ 视频质量模糊
**原因**: CRF 值设置过高
**解决**: 降低 `video_quality` 参数（如 23 → 20）

---

## 🔮 未来扩展方向

### 已规划（未实现）
- [ ] **时间轴图片切换**: 根据 JSON 描述在不同时间点切换背景图片
  ```json
  {
    "timeline": [
      {"start": "00:00", "end": "01:05", "image": "intro.jpg", "transition": "fade"},
      {"start": "01:05", "end": "02:30", "image": "main.jpg", "transition": "slide"}
    ]
  }
  ```
- [ ] **文字字幕叠加**: 自动生成字幕轨道
- [ ] **Logo 水印**: 在视频角落添加台标
- [ ] **多语言标题**: 支持中英双语标题

### 技术储备
这些功能都可以用 ffmpeg 实现，预留接口：
```python
# 时间轴切换（复杂滤镜链）
def generate_video_with_timeline(self, timeline: dict):
    pass

# 字幕叠加
def add_subtitles(self, srt_file: Path):
    pass
```

---

## 📚 参考资源

- **ffmpeg 官方文档**: https://ffmpeg.org/documentation.html
- **音频可视化滤镜**: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters
  - `showwaves`: 波形图
  - `showfreqs`: 频谱图
  - `avectorscope`: 矢量示波器
  - `showcqt`: 恒定Q变换频谱
- **Unsplash API**: https://source.unsplash.com/

---

## 💬 使用建议

1. **首次使用**: 运行 `.\生成视频.ps1` 测试所有效果
2. **选择风格**: 根据内容类型选择可视化效果
   - 新闻播报 → `wave` + `tech`
   - 音乐节目 → `spectrum` + `gradient`
   - 采访播客 → `wave` + `default`
3. **优化性能**: 
   - 测试时用 CRF=25（快速）
   - 发布时用 CRF=20（高质量）
4. **批量生成**: 修改 `generate_video.py` 的 `configs` 列表自定义输出版本

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Author**: IRC Agent Team
