# News Broadcast Automation Script (Windows PowerShell)
# 
# 完整工作流（6步）:
#   1. Fetch News         - 抓取新闻数据
#   2. Generate Broadcast - 生成播报脚本
#   3. Generate Audio     - 文本转语音（含时间轴）
#   4. Assign Images      - 配置图片（AI搜索+下载）
#   5. Generate Video     - 生成视频（支持时间轴多图切换）
#   6. Add BGM to Video   - 为视频添加背景音乐
#
# 参数说明:
#   -SkipFetch       : 跳过新闻抓取
#   -SkipBroadcast   : 跳过播报脚本生成
#   -SkipAudio       : 跳过音频生成
#   -SkipImages      : 跳过图片配置
#   -SkipBGM         : 跳过BGM添加
#   -SkipVideo       : 跳过视频生成
#   -UseTimeline     : 使用时间轴视频生成器（多图切换）
#   -BGMVolume       : BGM音量（0.0-1.0，默认0.15）
#
# 使用示例:
#   .\run_workflow.ps1                               # 完整流程（传统模式）
#   .\run_workflow.ps1 -UseTimeline                  # 完整流程（时间轴模式）⭐推荐
#   .\run_workflow.ps1 -SkipFetch -UseTimeline       # 跳过抓新闻
#   .\run_workflow.ps1 -UseTimeline -BGMVolume 0.2   # 调整BGM音量

param(
    [switch]$SkipFetch,
    [switch]$SkipBroadcast,
    [switch]$SkipAudio,
    [switch]$SkipImages,
    [switch]$SkipBGM,
    [switch]$SkipVideo,
    [double]$BGMVolume = 0.15,
    [switch]$UseTimeline
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEWS BROADCAST WORKFLOW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$NEWS_VIEWER_DIR = $PSScriptRoot
$PYTHON = Join-Path $ROOT_DIR ".venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON)) {
    Write-Host "[ERROR] Virtual environment not found" -ForegroundColor Red
    Write-Host "   Please run: uv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Python: $PYTHON" -ForegroundColor Green
Write-Host ""

Set-Location $NEWS_VIEWER_DIR

# Step 1: Fetch News
if (-not $SkipFetch) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 1/6: Fetch News" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    & $PYTHON "fetch_news.py"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] News fetch failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] News fetch completed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[SKIP] News fetch" -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Generate Broadcast
if (-not $SkipBroadcast) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 2/6: Generate Broadcast" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    & $PYTHON "generate_broadcast.py"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Broadcast failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Broadcast completed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[SKIP] Broadcast" -ForegroundColor Gray
    Write-Host ""
}

# Step 3: Generate Audio
if (-not $SkipAudio) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 3/6: Generate Audio" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    & $PYTHON "generate_audio.py"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Audio failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Audio completed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[SKIP] Audio" -ForegroundColor Gray
    Write-Host ""
}

# Step 4: Assign Images
if (-not $SkipImages) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 4/6: Assign Images" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    & $PYTHON "assign_images.py"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Image assignment failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Image assignment completed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[SKIP] Image assignment" -ForegroundColor Gray
    Write-Host ""
}

# Step 5: Generate Video
if (-not $SkipVideo) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 5/6: Generate Video" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    if ($UseTimeline) {
        Write-Host "[INFO] Using timeline video generator (multiple images)" -ForegroundColor Cyan
    } else {
        Write-Host "[INFO] Using optimized video generator" -ForegroundColor Cyan
    }
    
    & $PYTHON "generate_video_optimized.py"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Video generation failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Video generation completed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[SKIP] Video generation" -ForegroundColor Gray
    Write-Host ""
}

# Step 6: Add BGM to Video
if (-not $SkipBGM -and -not $SkipVideo) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 6/6: Add BGM to Video" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    $bgmDir = Join-Path $NEWS_VIEWER_DIR "bgm"
    $bgmFiles = Get-ChildItem -Path $bgmDir -Filter "*.mp3" -ErrorAction SilentlyContinue
    
    if ($bgmFiles.Count -eq 0) {
        Write-Host "[WARN] No BGM files found, skipping video BGM" -ForegroundColor Yellow
    } else {
        & $PYTHON "add_bgm_to_video.py" "--volume" $BGMVolume
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Video BGM addition failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "[OK] Video BGM added successfully" -ForegroundColor Green
    }
    
    Write-Host ""
} else {
    Write-Host "[SKIP] Video BGM" -ForegroundColor Gray
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Green
Write-Host "COMPLETED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$broadcastsDir = Join-Path $NEWS_VIEWER_DIR "broadcasts"
$latestDir = Get-ChildItem -Path $broadcastsDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestDir) {
    Write-Host "Output Directory: $($latestDir.Name)" -ForegroundColor Cyan
    Write-Host ""
    
    $files = Get-ChildItem -Path $latestDir.FullName -Filter "*.mp3"
    $videoFiles = Get-ChildItem -Path $latestDir.FullName -Filter "*.mp4"
    
    if ($files.Count -gt 0 -or $videoFiles.Count -gt 0) {
        Write-Host "Generated Files:" -ForegroundColor Cyan
        
        # 显示音频文件
        foreach ($file in $files) {
            $sizeMB = [math]::Round($file.Length / 1MB, 2)
            $icon = if ($file.Name -like "*full_with_bgm*") { "[BGM]" } elseif ($file.Name -like "*full.mp3") { "[Audio]" } else { "[Sound]" }
            Write-Host "  $icon $($file.Name) ($sizeMB MB)"
        }
        
        # 显示视频文件（按优先级排序）
        $priorityOrder = @("*with_bgm.mp4", "*with_effects.mp4", "*merged.mp4", "*.mp4")
        $displayedVideos = @{}
        
        foreach ($pattern in $priorityOrder) {
            $matchedVideos = $videoFiles | Where-Object { $_.Name -like $pattern } | Sort-Object LastWriteTime -Descending
            foreach ($file in $matchedVideos) {
                if (-not $displayedVideos.ContainsKey($file.FullName)) {
                    $sizeMB = [math]::Round($file.Length / 1MB, 2)
                    $icon = if ($file.Name -like "*with_bgm*") { "[Video+BGM]" } elseif ($file.Name -like "*with_effects*") { "[Video+FX]" } elseif ($file.Name -like "*merged*") { "[Video]" } else { "[Media]" }
                    Write-Host "  $icon $($file.Name) ($sizeMB MB)"
                    $displayedVideos[$file.FullName] = $true
                }
            }
        }
        
        Write-Host ""
        
        # 显示最终成品路径
        $finalAudio = $files | Where-Object { $_.Name -like "*full_with_bgm*" } | Select-Object -First 1
        if (-not $finalAudio) {
            $finalAudio = $files | Where-Object { $_.Name -like "*full.mp3" } | Select-Object -First 1
        }
        
        $finalVideo = $videoFiles | Where-Object { $_.Name -like "*with_bgm.mp4" } | Select-Object -First 1
        if (-not $finalVideo) {
            $finalVideo = $videoFiles | Where-Object { $_.Name -like "*with_effects.mp4" } | Select-Object -First 1
        }
        if (-not $finalVideo) {
            $finalVideo = $videoFiles | Where-Object { $_.Name -like "*merged.mp4" } | Select-Object -First 1
        }
        if (-not $finalVideo -and $videoFiles.Count -gt 0) {
            $finalVideo = $videoFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        }
        
        if ($finalAudio) {
            Write-Host "[Audio] Final Audio: $($finalAudio.FullName)" -ForegroundColor Green
        }
        
        if ($finalVideo) {
            Write-Host "[Video] Final Video: $($finalVideo.FullName)" -ForegroundColor Green
        }
        
        Write-Host ""
    }
}

Write-Host "Done!" -ForegroundColor Green
