# 视频生成快速测试
# 直接处理最新的播报，生成多种效果的视频

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEWS VIDEO GENERATOR - QUICK TEST" -ForegroundColor Cyan
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

Set-Location $NEWS_VIEWER_DIR

Write-Host "🎬 开始生成视频..." -ForegroundColor Yellow
Write-Host ""

& $PYTHON "generate_video.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ 视频生成完成!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # 显示输出文件
    $broadcastsDir = Join-Path $NEWS_VIEWER_DIR "broadcasts"
    $latestDir = Get-ChildItem -Path $broadcastsDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($latestDir) {
        $videoFiles = Get-ChildItem -Path $latestDir.FullName -Filter "*.mp4"
        
        if ($videoFiles.Count -gt 0) {
            Write-Host ""
            Write-Host "📂 输出目录: $($latestDir.FullName)" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "生成的视频:" -ForegroundColor Cyan
            foreach ($file in $videoFiles) {
                $sizeMB = [math]::Round($file.Length / 1MB, 2)
                Write-Host "  🎬 $($file.Name) ($sizeMB MB)" -ForegroundColor White
            }
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ 视频生成失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
