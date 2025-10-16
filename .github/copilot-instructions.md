# IRC AI Agent - Copilot Instructions

## 项目概览
这是一个实验性的多 AI Agent IRC 聊天协作系统。三个具有不同人格的 AI Agent（明轩、悦然、志远）同时连接到同一个 IRC 频道，使用不同的 LLM 模型和人格设定进行自然对话。

## 核心架构

### 多 Agent 系统设计

### Agent 人格配置（关键差异）
| Agent | 昵称 | 城市 | 模型 | API | 风格 | Temperature |
|-------|------|------|------|-----|------|-------------|
| 明轩 (mingxuan) | mingxuan | 北京 | gpt-4o-mini | OpenAI | 专业理性，4-5句 | 0.7 |
| 悦然 (yueran) | yueran | 深圳 | gpt-4o-mini | OpenAI | 活泼幽默，2-3句+emoji | 0.8 |
| 志远 (zhiyuan) | zhiyuan | 上海 | Ling-1T | TBox API | 沉稳务实，1-2句 | 0.6 |

## 核心技术实现

### 1. 智能响应判断 (`ai_agent.py::should_respond()`)

### 2. 时间感知系统 (重要特性)

### 3. 括号清理机制 (`remove_parenthetical_content()`)

### 4. 对话历史管理

### 5. 向量记忆系统 (实验性功能)

## 开发工作流

### 添加新 Agent
1. 复制 `configX.py` 和 `mainX.py`（X 为数字）
2. 修改 `IRCConfig.nickname` 和 `AgentConfig.system_prompt`
3. 更新所有 `ai_agent.py` 中的 `KNOWN_BOTS` 列表
4. 创建对应的 `start_botX.ps1` 启动脚本

### 运行和调试
```powershell
# 启动单个 Agent
uv run python main.py          # 明轩
uv run python main2.py         # 悦然
uv run python main3.py         # 志远

# 或使用脚本
.\start_bot2.ps1
.\start_bot3.ps1

# 测试 API 连接
uv run python test_ling.py                # 测试 Ling-1T API
uv run python debug_ling_response.py      # 调试 Ling API 响应

# 检查 Agent 信息
uv run python show_agents_info.py         # 显示所有 Agent 配置
```

### 测试框架
  - `test_clean_brackets.py` - 括号清理功能
  - `test_user_detection.py` - 人类用户检测
  - `test_time_awareness.py` - 时间感知系统
  - `test_time_injection.py` - 时间注入机制

## 项目特定约定

### 环境变量 (`.env`)
```bash
# OpenAI (明轩/悦然)
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选

# Ling API (志远)
LING_API_KEY=xxx
LING_BASE_URL=https://api.tbox.cn/api/llm/v1/

# IRC 配置
IRC_SERVER=irc.lemonhall.me
IRC_PORT=6667
IRC_CHANNEL=ai-collab-test
IRC_SASL_USERNAME=  # 可选
IRC_SASL_PASSWORD=  # 可选
```

### 系统提示编写准则

### 频道名称规范

## 常见陷阱

1. **忘记更新 KNOWN_BOTS**：添加新 Agent 后必须在 `ai_agent.py` 中更新列表，否则会被识别为人类
2. **大小写敏感**：用户名比较使用 `.lower()`，但配置文件中的昵称本身区分大小写
3. **括号清理过激**：如果 AI 需要在回复中使用括号（如数学表达式），需要修改 `remove_parenthetical_content()`
4. **API 配置混淆**：志远使用 `LING_API_KEY`，其他两个用 `OPENAI_API_KEY`
5. **KeyboardInterrupt 处理**：使用 `os._exit(0)` 强制退出，因为 miniirc 的线程可能阻塞普通退出

## 项目依赖

## 关键文件架构图解

```
irc_agent/
├── main.py, main2.py, main3.py     # 三个独立的 Agent 入口点
├── config.py, config2.py, config3.py  # 对应的配置文件
├── ai_agent.py                      # 核心 AI 逻辑（共享）
├── irc_client.py                    # IRC 连接管理（共享）
├── memory_system.py                 # 长期记忆系统（实验性）
├── test_*.py                        # 单元测试套件
└── start_bot*.ps1                   # PowerShell 启动脚本
```

## 未来扩展方向

## 关键开发模式

### 错误处理模式

### 消息流设计模式
1. **接收** → IRC 客户端捕获消息
2. **判断** → `should_respond()` 决定是否回应
3. **处理** → `generate_response()` 生成回复
4. **清理** → `remove_parenthetical_content()` 移除括号
5. **发送** → 返回给 IRC 客户端

### 状态管理模式
