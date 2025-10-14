# 新闻播报视频生成工作流程图

## 完整流程（时间轴多图模式）

```
┌─────────────────────────────────────────────────────────────────────┐
│                     新闻播报视频生成流程                              │
└─────────────────────────────────────────────────────────────────────┘

1️⃣ 抓取新闻
   fetch_news.py
   ↓
   news.json (新闻数据)

2️⃣ 生成播报脚本
   generate_broadcast.py
   ↓
   broadcasts/20251014_081240/broadcast.json (结构化播报稿)
   broadcasts/20251014_081240/broadcast.txt (纯文本)

3️⃣ 文本转语音
   generate_audio.py
   ↓
   broadcast_00_intro.mp3 (开场白)
   broadcast_01_world.mp3 (世界新闻)
   broadcast_02_asia.mp3 (亚太新闻)
   ...
   broadcast_full.mp3 (完整音频)
   + 回写时间轴到 broadcast.json (start_time, end_time)

4️⃣ AI配置图片 ⭐
   assign_images.py
   ↓
   → DeepSeek 分析内容 → 生成搜索关键词
   → Unsplash 搜索 → 下载图片
   ↓
   image_01_world.jpg
   image_02_asia.jpg
   image_03_americas.jpg
   ...
   + 更新 broadcast.json (image_file 字段)

5️⃣ 添加音频BGM
   add_bgm.py --volume 0.15
   ↓
   broadcast_full_with_bgm.mp3 (人声+BGM混音)

6️⃣ 生成时间轴视频 ⭐
   generate_video_optimized.py
   
   ┌─────────────────────────────────────────┐
   │ 第一阶段：分段生成                       │
   │                                         │
   │  broadcast_00_intro.mp3 + intro_bg.jpg  │
   │  → ffmpeg (图片+音频) → temp_video_00.mp4│
   │                                         │
   │  broadcast_01_world.mp3 + image_01.jpg  │
   │  → ffmpeg (图片+音频) → temp_video_01.mp4│
   │                                         │
   │  broadcast_02_asia.mp3 + image_02.jpg   │
   │  → ffmpeg (图片+音频) → temp_video_02.mp4│
   │                                         │
   │  ... (所有片段)                          │
   └─────────────────────────────────────────┘
   ↓
   ┌─────────────────────────────────────────┐
   │ 第二阶段：拼接合并                       │
   │                                         │
   │  temp_video_00.mp4                      │
   │  temp_video_01.mp4                      │
   │  temp_video_02.mp4                      │
   │  ...                                    │
   │  → ffmpeg concat → video_full_merged.mp4│
   └─────────────────────────────────────────┘
   ↓
   ┌─────────────────────────────────────────┐
   │ 第三阶段：添加音频可视化特效              │
   │                                         │
   │  video_full_merged.mp4                  │
   │  → ffmpeg (波形/频谱)                    │
   │  → video_full_with_effects.mp4          │
   └─────────────────────────────────────────┘
   ↓
   清理临时文件 (temp_video_*.mp4)

7️⃣ 添加视频BGM ⭐
   add_bgm_to_video.py --volume 0.15
   
   video_full_with_effects.mp4 (人声+特效)
   + bgm/xxx.mp3
   → ffmpeg (音频混音，视频直接复制)
   ↓
   video_full_with_effects_with_bgm.mp4 ✅ 最终成品

┌─────────────────────────────────────────────────────────────────────┐
│                         最终输出                                     │
│                                                                     │
│  📹 video_full_with_effects_with_bgm.mp4                            │
│     - 多图背景（随新闻切换）                                         │
│     - 人声播报                                                       │
│     - 音频可视化特效（波形）                                         │
│     - 背景音乐                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## 性能优势

### 传统方案（废弃）
```
每个片段: (音频 + 图片 + 特效处理) → 慢 ❌
拼接: 所有片段 → video.mp4
添加BGM: 重新编码整个视频 → 极慢 ❌
总耗时: ~10-15分钟
```

### 优化方案（当前）✅
```
第一阶段: (音频 + 图片) → 快 ⚡
         每个片段只做简单合成，无特效
         
第二阶段: 拼接所有片段 → 快 ⚡
         
第三阶段: 一次性添加特效 → 中等 ⏱️
         只处理一个完整视频
         
第四阶段: 添加BGM → 极快 ⚡⚡
         视频不重新编码，只混音
         
总耗时: ~3-5分钟
```

## 关键技术点

### 1. 分段生成（图片+音频）
```bash
ffmpeg -i audio_01.mp3 -loop 1 -i image_01.jpg \
       -shortest -c:v libx264 -c:a aac \
       temp_video_01.mp4
```
- ✅ 无复杂滤镜
- ✅ 编码速度快
- ✅ 文件小

### 2. 无损拼接
```bash
ffmpeg -f concat -i filelist.txt \
       -c copy video_merged.mp4
```
- ✅ 不重新编码
- ✅ 速度极快

### 3. 统一添加特效
```bash
ffmpeg -i video_merged.mp4 \
       -filter_complex "[0:a]showwaves=...[wave];[0:v][wave]overlay" \
       video_with_effects.mp4
```
- ✅ 一次性处理
- ✅ 特效统一

### 4. BGM混音（视频不动）
```bash
ffmpeg -i video.mp4 -stream_loop -1 -i bgm.mp3 \
       -filter_complex "[0:a][1:a]amix..." \
       -c:v copy \  # 视频直接复制，不编码！
       video_with_bgm.mp4
```
- ⚡ 视频不重新编码
- ⚡ 速度极快（只处理音频）

## 一键运行

```powershell
# 完整流程
.\run_workflow.ps1 -UseTimeline

# 只重新生成视频部分
.\run_workflow.ps1 -SkipFetch -SkipBroadcast -SkipAudio -UseTimeline
```

## 文件大小对比

| 文件 | 大小 | 说明 |
|------|------|------|
| broadcast_full.mp3 | ~5 MB | 纯人声音频 |
| broadcast_full_with_bgm.mp3 | ~5 MB | 人声+BGM |
| image_*.jpg | ~200 KB/张 | 背景图片 |
| video_full_merged.mp4 | ~80 MB | 合并后视频（无特效）|
| video_full_with_effects.mp4 | ~120 MB | 添加特效后 |
| video_full_with_effects_with_bgm.mp4 | ~120 MB | 最终版本 |

## 未来优化方向

- [ ] 并行生成视频片段（多进程）
- [ ] GPU 加速编码（-hwaccel）
- [ ] 更快的编码参数（-preset ultrafast）
- [ ] 图片缓存和复用
- [ ] 增量更新（只重新生成变化的片段）
