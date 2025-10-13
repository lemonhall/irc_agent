#!/usr/bin/env python3
"""简单的Web服务器，用于查看Agent的历史记忆"""

import json
import os
import tempfile
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def read_agent_status(nickname):
    """从文件读取agent状态"""
    status_file = os.path.join(tempfile.gettempdir(), f"irc_agent_{nickname}.json")
    
    try:
        if not os.path.exists(status_file):
            return None
        
        with open(status_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"读取 {nickname} 状态文件失败: {e}")
        return None

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/agents')
def get_agents():
    """获取所有agent状态的API"""
    agents_data = {}
    
    # 读取三个agent的状态文件
    for nickname in ['mingxuan', 'yueran', 'zhiyuan']:
        data = read_agent_status(nickname)
        if data:
            agents_data[nickname] = data
    
    return jsonify(agents_data)

@app.route('/api/agents/<agent_name>')
def get_agent(agent_name):
    """获取特定agent状态的API"""
    data = read_agent_status(agent_name)
    
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Agent not found'}), 404

def start_web_server():
    """启动web服务器"""
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    print("启动Agent监控Web服务器...")
    print("访问 http://127.0.0.1:5000 查看Agent状态")
    start_web_server()