#!/usr/bin/env python3
"""启动Web监控服务器"""

import subprocess
import sys
import os

# 检查并安装 flask
try:
    import flask
except ImportError:
    print("正在安装 Flask...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

# 启动web服务器
if __name__ == "__main__":
    print("启动IRC Agent监控面板...")
    print("请在浏览器中访问: http://127.0.0.1:5000")
    
    # 切换到web目录
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    # 启动Flask应用
    from app import start_web_server
    start_web_server()