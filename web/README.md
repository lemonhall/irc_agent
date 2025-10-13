# IRC Agent 监控面板

## 功能
- 实时查看三个Agent（mingxuan、yueran、zhiyuan）的状态
- 查看各Agent的对话历史记录
- 监控Agent的在线状态和最后活动时间
- 查看各Agent的配置参数

## 使用方法

### 1. 启动Agent
首先启动你想监控的Agent：
```bash
# 启动明轩
uv run python main.py

# 启动悦然  
uv run python main2.py

# 启动志远
uv run python main3.py
```

### 2. 启动监控面板
```bash
# 切换到web目录
cd web

# 启动监控服务器
uv run python start_monitor.py
```

### 3. 查看监控面板
在浏览器中访问：http://127.0.0.1:5000

## 界面功能
- **实时状态**：显示Agent是否在线（1分钟内有活动算在线）
- **对话历史**：显示每个Agent的完整对话历史
- **参数监控**：显示最大连续轮数、历史消息数等参数
- **自动刷新**：每10秒自动更新数据
- **手动刷新**：点击右下角的刷新按钮

## API接口
- `GET /api/agents` - 获取所有Agent状态
- `GET /api/agents/<agent_name>` - 获取特定Agent状态

## 注意事项
- Agent必须先启动，监控面板才能看到数据
- 如果Agent重启，历史记录会重置
- 监控面板不会影响Agent的正常运行