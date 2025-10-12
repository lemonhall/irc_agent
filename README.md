# IRC AI Agent

一个实验性项目，让 AI Agent 加入 IRC 聊天室，与人类和其他 agent 协作完成任务。

## 功能特性

- 🤖 基于 OpenAI API 的智能对话
- 💬 连接到现有 IRC 服务器和频道
- 🎯 支持关键词触发和 @提及响应
- 📝 维护对话上下文
- 🔧 灵活的配置系统

## 快速开始

### 1. 安装依赖

```bash
uv add openai miniirc
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 OpenAI API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
OPENAI_API_KEY=sk-your-actual-api-key
```

### 3. 配置 IRC 连接

编辑 `config.py` 文件，修改 IRC 连接参数：

```python
@dataclass
class IRCConfig:
    server: str = "irc.libera.chat"  # 你的 IRC 服务器
    port: int = 6667
    nickname: str = "my_ai_bot"      # Bot 的昵称
    channel: str = "#your-channel"    # 要加入的频道
    use_ssl: bool = False
```

### 4. 运行

```bash
uv run python main.py
```

## 使用方法

Bot 会在以下情况下响应：

1. **提及 Bot 名字**：在消息中包含 bot 的昵称
   ```
   my_ai_bot: 你好！
   ```

2. **触发关键词**：消息包含预设的关键词（默认：help, 帮助, 协作）
   ```
   有人能帮助我吗？
   ```

## 项目结构

```
irc_agent/
├── main.py           # 主程序入口
├── config.py         # 配置文件
├── irc_client.py     # IRC 客户端封装
├── ai_agent.py       # AI Agent 实现
├── .env.example      # 环境变量示例
└── README.md         # 本文件
```

## 自定义配置

### 修改 Agent 行为

在 `config.py` 中的 `AgentConfig` 类：

```python
@dataclass
class AgentConfig:
    trigger_on_mention: bool = True  # 是否在提及时响应
    trigger_keywords: list[str] = None  # 触发关键词列表
    system_prompt: str = """..."""  # 系统提示词
```

### 修改 OpenAI 模型

在 `config.py` 中的 `OpenAIConfig` 类：

```python
@dataclass
class OpenAIConfig:
    model: str = "gpt-4o-mini"  # 或 "gpt-4o", "gpt-3.5-turbo" 等
    max_tokens: int = 500
    temperature: float = 0.7
```

## 下一步开发

这是一个 MVP 版本，可以扩展的方向：

- [ ] 多 Agent 协作机制
- [ ] 任务分配和跟踪
- [ ] 更复杂的记忆系统（向量数据库）
- [ ] 支持命令系统（如 !reset, !status）
- [ ] 日志和对话记录持久化
- [ ] Web 界面监控
- [ ] 支持多个频道

## 注意事项

- 确保你有权限在目标 IRC 频道使用 Bot
- 注意 API 调用成本，建议使用 gpt-4o-mini
- Bot 会记住最近 20 条对话历史

## License

MIT
