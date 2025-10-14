# News Broadcast Automation Script (Windows PowerShell)
# Workflow: Fetch News -> Generate Script -> Generate Audio -> Add BGM

param(
    [switch]$SkipFetch,
    [switch]$SkipBroadcast,
    [switch]$SkipAudio,
    [switch]$SkipBGM,
    [double]$BGMVolume = 0.15
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
    Write-Host "STEP 1/4: Fetch News" -ForegroundColor Yellow
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
    Write-Host "STEP 2/4: Generate Broadcast" -ForegroundColor Yellow
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
    Write-Host "STEP 3/4: Generate Audio" -ForegroundColor Yellow
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

# Step 4: Add BGM
if (-not $SkipBGM) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 4/4: Add BGM" -ForegroundColor Yellow
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
    if ($files.Count -gt 0) {
        Write-Host "Files:" -ForegroundColor Cyan
        foreach ($file in $files) {
            $sizeMB = [math]::Round($file.Length / 1MB, 2)
            Write-Host "  - $($file.Name) ($sizeMB MB)"
        }
        Write-Host ""
        
        $fullAudio = $files | Where-Object { $_.Name -like "*full_with_bgm*" } | Select-Object -First 1
        if (-not $fullAudio) {
            $fullAudio = $files | Where-Object { $_.Name -like "*full.mp3" } | Select-Object -First 1
        }
        
        if ($fullAudio) {
            Write-Host "Output File: $($fullAudio.FullName)" -ForegroundColor Gray
            Write-Host ""
        }
    }
}

Write-Host "Done!" -ForegroundColor Green
