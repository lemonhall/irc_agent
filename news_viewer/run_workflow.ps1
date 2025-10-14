# News Broadcast Automation Script (Windows PowerShell)
# Workflow: Fetch News -> Generate Script -> Generate Audio -> Add BGM

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

# Step 5: Add BGM
if (-not $SkipBGM) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 5/6: Add BGM" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    $bgmDir = Join-Path $NEWS_VIEWER_DIR "bgm"
    $bgmFiles = Get-ChildItem -Path $bgmDir -Filter "*.mp3" -ErrorAction SilentlyContinue
    
    if ($bgmFiles.Count -eq 0) {
        Write-Host "[WARN] No BGM files" -ForegroundColor Yellow
    } else {
        & $PYTHON "add_bgm.py" "--volume" $BGMVolume
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] BGM failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "[OK] BGM completed" -ForegroundColor Green
    }
    
    Write-Host ""
} else {
    Write-Host "[SKIP] BGM" -ForegroundColor Gray
    Write-Host ""
}

# Step 6: Generate Video
if (-not $SkipVideo) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 6/6: Generate Video" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    if ($UseTimeline) {
        Write-Host "[INFO] Using timeline video generator (multiple images)" -ForegroundColor Cyan
        & $PYTHON "generate_video_with_timeline.py"
    } else {
        Write-Host "[INFO] Using standard video generator (single image)" -ForegroundColor Cyan
        & $PYTHON "generate_video.py"
    }
    
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

# Summary
Write-Host "========================================" -ForegroundColor Green
Write-Host "COMPLETED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$broadcastsDir = Join-Path $NEWS_VIEWER_DIR "broadcasts"
$latestDir = Get-ChildItem -Path $broadcastsDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestDir) {
    Write-Host "Output: $($latestDir.Name)" -ForegroundColor Cyan
    Write-Host ""
    
    $files = Get-ChildItem -Path $latestDir.FullName -Filter "*.mp3"
    $videoFiles = Get-ChildItem -Path $latestDir.FullName -Filter "*.mp4"
    
    if ($files.Count -gt 0 -or $videoFiles.Count -gt 0) {
        Write-Host "Files:" -ForegroundColor Cyan
        
        # 显示音频文件
        foreach ($file in $files) {
            $sizeMB = [math]::Round($file.Length / 1MB, 2)
            Write-Host "  🎵 $($file.Name) ($sizeMB MB)"
        }
        
        # 显示视频文件
        foreach ($file in $videoFiles) {
            $sizeMB = [math]::Round($file.Length / 1MB, 2)
            Write-Host "  🎬 $($file.Name) ($sizeMB MB)"
        }
        Write-Host ""
        
        $fullAudio = $files | Where-Object { $_.Name -like "*full_with_bgm*" } | Select-Object -First 1
        if (-not $fullAudio) {
            $fullAudio = $files | Where-Object { $_.Name -like "*full.mp3" } | Select-Object -First 1
        }
        
        if ($fullAudio) {
            Write-Host "Audio File: $($fullAudio.FullName)" -ForegroundColor Gray
        }
        
        if ($videoFiles.Count -gt 0) {
            Write-Host "Video File: $($videoFiles[0].FullName)" -ForegroundColor Gray
        }
        
        Write-Host ""
    }
}

Write-Host "Done!" -ForegroundColor Green
