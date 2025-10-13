# 新闻播报音频生成脚本
Write-Host "🎤 新闻播报音频生成工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 检查虚拟环境
$venvPath = Join-Path $PSScriptRoot ".." ".venv" "Scripts" "python.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host "❌ 虚拟环境不存在，请先运行: uv venv" -ForegroundColor Red
    exit 1
}

# 检查API Key
if (-not $env:DASHSCOPE_API_KEY) {
    Write-Host "❌ 未设置DASHSCOPE_API_KEY环境变量" -ForegroundColor Red
    Write-Host "请运行: `$env:DASHSCOPE_API_KEY='your-api-key'" -ForegroundColor Yellow
    exit 1
}

# 运行转换脚本
Write-Host "`n🚀 启动TTS转换..." -ForegroundColor Green

# 如果提供了参数，传递给Python脚本
if ($args.Count -gt 0) {
    & $venvPath (Join-Path $PSScriptRoot "text_to_speech.py") $args[0]
} else {
    & $venvPath (Join-Path $PSScriptRoot "text_to_speech.py")
}

Write-Host "`n✨ 完成！" -ForegroundColor Green
