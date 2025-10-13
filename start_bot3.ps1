# 启动第三个 AI Agent (智渊 - 使用 Ling-1T 模型)
Write-Host "正在启动 IRC AI Agent 3 (智渊 - Ling-1T)..." -ForegroundColor Cyan

# 检查虚拟环境
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "✓ 找到虚拟环境" -ForegroundColor Green
    & .venv\Scripts\python.exe main3.py
} else {
    Write-Host "✗ 未找到虚拟环境，使用系统 Python" -ForegroundColor Yellow
    python main3.py
}
