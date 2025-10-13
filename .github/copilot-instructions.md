# IRC AI Agent - Copilot Instructions

## 项目概览
这是一个实验性的多 AI Agent IRC 聊天协作系统。三个具有不同人格的 AI Agent（明轩、悦然、志远）同时连接到同一个 IRC 频道，使用不同的 LLM 模型和人格设定进行自然对话。

## 核心架构

### 多 Agent 系统设计
- **三个独立进程**：每个 Agent 通过独立的 `main.py`/`main2.py`/`main3.py` 运行
- **配置隔离**：`config.py`/`config2.py`/`config3.py` 为每个 Agent 定义不同的人格、模型和行为
- **共享代码**：`irc_client.py` 和 `ai_agent.py` 被所有 Agent 复用
- **启动方式**：使用 PowerShell 脚本 `start_bot2.ps1`/`start_bot3.ps1` 启动（或直接 `uv run python main.py`）

### Agent 人格配置（关键差异）
| Agent | 昵称 | 城市 | 模型 | 风格 | Temperature |
|-------|------|------|------|------|-------------|
| 明轩 (mingxuan) | mingxuan | 北京 | gpt-4o-mini | 专业理性，4-5句 | 0.7 |
| 悦然 (yueran) | yueran | 深圳 | gpt-4o-mini | 活泼幽默，2-3句+emoji | 0.8 |
| 志远 (zhiyuan) | zhiyuan | 上海 | Ling-1T | 沉稳务实，1-2句 | 0.6 |

## 核心技术实现

### 1. 智能响应判断 (`ai_agent.py::should_respond()`)
- **AI 驱动**：使用 LLM 判断是否应该回应（不是简单的关键词匹配）
- **人类检测**：通过白名单 `KNOWN_BOTS = ["mingxuan", "yueran", "zhiyuan"]` 识别人类用户
- **防止刷屏**：随机 1-3 轮的 `max_bot_turns`，达到阈值后只对人类或 @ 提及响应
- **降级机制**：AI 判断失败时降级到 `trigger_keywords` 关键词触发

### 2. 时间信息注入
- **动态注入**：每次 API 调用时在系统提示末尾添加 `[当前时间：2025年10月13日 9点35分]`
- **位置**：`generate_response()` 和 `should_respond()` 中的 `messages_with_time`
- **不污染历史**：使用 `copy()` 创建临时列表，原始 `conversation_history` 不包含时间

### 3. 括号清理机制 (`remove_parenthetical_content()`)
- **目的**：防止 AI 添加舞台指示或元评论，如 `(注：xxx)` 或 `(思考片刻)`
- **实现**：正则 `r'[（(][^）)]*[）)]'` 移除所有中英文括号及其内容
- **应用时机**：`generate_response()` 返回前自动清理所有括号内容

### 4. 对话历史管理
- **容量**：`max_history = 20`，保留系统提示 + 最近 19 条消息
- **格式**：`[来自 {sender} 在 {channel}]: {message}` 提供上下文
- **轮数提示**：在最后一条消息添加 `[系统提示：这是最近第 X 轮 bot 连续对话...]`

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
```

### 测试
- **单元测试**：`test_*.py` 文件测试特定功能（如 `test_clean_brackets.py`、`test_user_detection.py`）
- **集成测试**：直接运行 Agent 并在 IRC 频道观察交互
- **模型测试**：`test_ling.py` 测试 Ling-1T API 连接

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
- **严禁括号**：在所有 `system_prompt` 中强调 "❌ 绝对不要用括号写旁白或舞台指示"
- **自然对话**：强调 "你是真实的聊天参与者，不是在演剧本"
- **暂停时机**：明确何时应该停止回复（如 "好的"、"谢谢" 等终止词）
- **时间感知**：不需要在提示中说明时间注入（系统自动处理）

### 频道名称规范
- IRC 频道必须以 `#` 开头
- `irc_client.py::normalize_channel()` 自动添加 `#` 前缀
- 配置文件中可以省略 `#`（如 `ai-collab-test` → `#ai-collab-test`）

## 常见陷阱

1. **忘记更新 KNOWN_BOTS**：添加新 Agent 后必须在 `ai_agent.py` 中更新列表，否则会被识别为人类
2. **大小写敏感**：用户名比较使用 `.lower()`，但配置文件中的昵称本身区分大小写
3. **括号清理过激**：如果 AI 需要在回复中使用括号（如数学表达式），需要修改 `remove_parenthetical_content()`
4. **API 配置混淆**：志远使用 `LING_API_KEY`，其他两个用 `OPENAI_API_KEY`
5. **KeyboardInterrupt 处理**：使用 `os._exit(0)` 强制退出，因为 miniirc 的线程可能阻塞普通退出

## 项目依赖
- **uv**：Python 包管理器（推荐）
- **miniirc**：轻量级 IRC 客户端库
- **openai**：OpenAI SDK（兼容 Ling API）
- **python-dotenv**：环境变量加载

## 未来扩展方向
- 向量数据库集成（长期记忆）
- 任务分配和跟踪系统
- 多频道支持
- Web 监控界面
- 命令系统（如 `!reset`、`!status`）
