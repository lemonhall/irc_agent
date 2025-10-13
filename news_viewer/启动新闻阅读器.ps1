# 新闻阅读器 - 一键启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   📰 新闻阅读器启动中..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 进入脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 运行 Python 脚本
uv run python run.py
