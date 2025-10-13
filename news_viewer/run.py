"""
一键运行：抓取新闻 + 启动服务器
"""
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def run_fetch_news():
    """运行新闻抓取"""
    print("=" * 60)
    print("📡 正在抓取新闻...")
    print("=" * 60)
    
    fetch_script = SCRIPT_DIR / "fetch_news.py"
    result = subprocess.run(
        [sys.executable, str(fetch_script)],
        cwd=str(SCRIPT_DIR)
    )
    
    if result.returncode != 0:
        print("\n❌ 新闻抓取失败，但仍然启动服务器（可能会显示旧数据）\n")
    else:
        print("\n✅ 新闻抓取成功！\n")

def start_server():
    """启动服务器"""
    print("=" * 60)
    print("🚀 正在启动服务器...")
    print("=" * 60)
    
    server_script = SCRIPT_DIR / "start_server.py"
    subprocess.run(
        [sys.executable, str(server_script)],
        cwd=str(SCRIPT_DIR)
    )

if __name__ == "__main__":
    # 先抓取新闻
    run_fetch_news()
    
    # 然后启动服务器
    start_server()
