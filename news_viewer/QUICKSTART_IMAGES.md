# 图片配置快速开始

## 第一步：配置完成 ✅

你的 `.env` 文件已经配置好了：
```bash
UNSPLASH_ACCESS_KEY=aeXMXauIrWa70uN-pxfv_uh9roLL1e3qy_xhzM9iE0g
```

## 第二步：运行完整工作流

### 方案 A：使用时间轴视频（推荐，支持多图片切换）

```powershell
# 切换到 news_viewer 目录
cd news_viewer

# 运行完整工作流
.\run_workflow.ps1 -UseTimeline
```

这个命令会依次执行：
1. ✅ 抓取新闻
2. ✅ 生成播报稿
3. ✅ 生成音频 + 时间轴
4. ✅ **AI 配置图片**（使用 Unsplash 搜索）
5. ✅ 添加背景音乐
6. ✅ **生成时间轴视频**（每个片段不同图片）

### 方案 B：只测试图片配置功能

如果你已经有了音频文件，只想测试图片配置：

```powershell
# 为最新的 broadcast 配置图片
uv run python assign_images.py

# 然后生成视频
uv run python generate_video_with_timeline.py
```

### 方案 C：跳过某些步骤（快速测试）

如果你只想重新配置图片和生成视频：

```powershell
.\run_workflow.ps1 -SkipFetch -SkipBroadcast -SkipAudio -SkipBGM -UseTimeline
```

## 第三步：查看结果

运行完成后，你会看到：

```
broadcasts/20251014_XXXXXX/
├── broadcast.json              # 包含图片路径信息
├── broadcast_full_with_bgm.mp3 # 音频文件
├── image_01_world.jpg          # 世界新闻图片
├── image_02_asia.jpg           # 亚太新闻图片
├── image_03_americas.jpg       # 美洲新闻图片
├── image_04_us.jpg             # 美国新闻图片
├── ...                         # 其他图片
└── video_full_timeline.mp4     # 🎬 最终视频！
```

## 预期效果

视频播放时，会根据时间轴自动切换背景图片：

```
0:00 - 0:04   → intro_background.jpg（固定图片）
0:04 - 0:40   → 世界新闻图片（AI 搜索）
0:40 - 1:17   → 亚太新闻图片（AI 搜索）
1:17 - 2:02   → 美洲新闻图片（AI 搜索）
...
```

每个图片上都会叠加音频波形或频谱效果！

## 故障排除

### 问题 1：Unsplash API 调用失败

**可能原因**：网络问题或 API 限制

**解决方案**：
```powershell
# 系统会自动降级到纯色背景
# 或者重新运行
uv run python assign_images.py
```

### 问题 2：图片下载慢

**原因**：Unsplash 服务器在国外

**解决方案**：耐心等待，或者使用代理

### 问题 3：想自定义固定图片

编辑 `assign_images.py`：

```python
# 第 18-19 行
INTRO_IMAGE = "intro_background.jpg"  # 改成你的图片文件名
OUTRO_IMAGE = "outro_background.jpg"  # 或 None 表示不使用
```

然后把图片文件放到 `news_viewer/` 目录下。

## 高级选项

### 更改视觉效果

编辑 `generate_video_with_timeline.py` 的 `main()` 函数：

```python
# 第 336 行
success = generator.generate_video_from_broadcast(
    broadcast_dir,
    effect="wave",        # 改成 "vectorscope"、"spectrum" 或 "none"
    color_scheme="default"  # 改成 "gradient"、"blue"、"gold"
)
```

### 更改视频质量

```python
# 在 generate_video_from_broadcast 调用中添加
video_quality=18  # 18=高质量大文件, 28=低质量小文件, 默认23
```

## 完整示例

```powershell
# 1. 进入目录
cd e:\development\irc_agent\news_viewer

# 2. 查看当前状态
uv run python test_image_config.py

# 3. 运行完整工作流（带时间轴视频）
.\run_workflow.ps1 -UseTimeline

# 4. 等待完成，视频会自动生成在 broadcasts/最新目录/ 下

# 5. 播放视频
explorer.exe broadcasts\最新目录\video_full_timeline.mp4
```

## 下一步

- ✅ 尝试不同的视觉效果（wave、vectorscope、spectrum）
- ✅ 自定义 intro/outro 固定图片
- ✅ 调整视频质量参数
- ✅ 查看 `IMAGE_CONFIG_GUIDE.md` 了解更多技术细节

祝你使用愉快！🎉
