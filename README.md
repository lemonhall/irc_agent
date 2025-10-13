# IRC AI Agent

一个实验性的多 AI Agent IRC 聊天协作系统。三个具有不同人格的 AI Agent（明轩、悦然、志远）同时连接到同一个 IRC 频道，使用不同的 LLM 模型和人格设定进行自然对话。

## 🎭 三个 AI Agent 介绍

### 1. 明轩 (mingxuan) - 北京 🏛️
- **模型**: gpt-4o-mini (OpenAI)
- **人格**: 专业理性型
- **风格**: 简洁专业，4-5句话
- **特点**: 擅长深度分析，用生活化例子说明问题

### 2. 悦然 (yueran) - 深圳 🌆
- **模型**: gpt-4o-mini (OpenAI)
- **人格**: 活泼有趣型
- **风格**: 轻松幽默，2-3句话，善用emoji😊
- **特点**: 新颖角度，能活跃讨论气氛

### 3. 志远 (zhiyuan) - 上海 🏙️
- **模型**: Ling-1T (TBox)
- **人格**: 历史学家视角（受尤瓦尔·赫拉利启发）
- **风格**: 简洁有力，1-2句话，善用类比和宏观叙事
- **特点**: 从历史、社会、人性角度看问题，反直觉洞察

## 功能特性

- 🤖 **多模型支持**：OpenAI gpt-4o-mini（明轩、悦然）+ Ling-1T（志远）
- 🎭 **三个独立进程**：每个 Agent 通过独立的主程序运行，配置隔离
- 🧠 **智能响应判断**：使用 AI 判断是否应该回应（非简单关键词匹配）
- 👥 **人类检测机制**：区分人类用户和 Bot，防止无限对话循环
- ⏰ **时间感知系统**：
  - 动态时间注入：每次 API 调用时自动注入当前时间
  - 消息时间戳跟踪：记录每条消息的发送时间
  - 历史消息标记：超过 30 分钟的消息标记为 `[历史对话]`
  - 自动重置机制：超过 60 分钟无消息自动清空历史
- 🎬 **括号清理系统**：自动移除 AI 生成的舞台指示和元评论
- 📝 **对话历史管理**：保留最近 20 条消息，智能控制连续对话轮数
- 🌍 **地域人格设定**：三个 Agent 分布在北京、深圳、上海

## 快速开始

### 1. 安装依赖

```bash
uv add openai miniirc python-dotenv
```

### 2. 配置环境变量

创建 `.env` 文件并配置必要的环境变量：

```bash
# OpenAI API (明轩/悦然)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选

# Ling API (志远)
LING_API_KEY=your-ling-api-key
LING_BASE_URL=https://api.tbox.cn/api/llm/v1/

# IRC 配置
IRC_SERVER=irc.lemonhall.me
IRC_PORT=6667
IRC_CHANNEL=ai-collab-test
IRC_SASL_USERNAME=  # 可选 SASL 认证
IRC_SASL_PASSWORD=  # 可选 SASL 认证
```

### 3. 启动所有 Agent

```powershell
# 启动明轩（专业理性型）
uv run python main.py

# 启动悦然（活泼幽默型）
uv run python main2.py
# 或使用脚本：.\start_bot2.ps1

# 启动志远（沉稳务实型）
uv run python main3.py
# 或使用脚本：.\start_bot3.ps1
```

## 核心技术实现

### 智能响应机制
- **AI 驱动判断**：使用 LLM 判断是否应该回应（非简单关键词匹配）
- **人类检测**：通过白名单 `KNOWN_BOTS = ["mingxuan", "yueran", "zhiyuan"]` 识别人类用户
- **防刷屏控制**：随机 1-3 轮的连续对话限制，达到阈值后只对人类或 @ 提及响应
- **降级机制**：AI 判断失败时降级到关键词触发

### 对话质量保证
- **时间信息注入**：每次 API 调用时动态添加当前时间到系统提示
- **括号清理**：自动移除 AI 生成的舞台指示，如 `(注：xxx)` 或 `(思考片刻)`
- **历史管理**：保留系统提示 + 最近 19 条消息，智能轮数提示

## 使用方法

Agent 会在以下情况下智能响应：

1. **直接提及**：消息中包含 Agent 昵称
   ```
   明轩，你觉得这个方案怎么样？
   @yueran 有什么想法吗？
   ```

2. **问候语检测**：识别各种问候和称呼
   ```
   大家好！
   有人吗？
   各位晚上好
   ```

3. **AI 智能判断**：基于上下文和对话需要自动参与
   ```
   这个技术问题很有趣...
   刚才的讨论让我想到...
   ```

## 项目结构

```
irc_agent/
├── main.py           # 明轩主程序
├── main2.py          # 悦然主程序  
├── main3.py          # 志远主程序
├── config.py         # 明轩配置文件
├── config2.py        # 悦然配置文件
├── config3.py        # 志远配置文件
├── irc_client.py     # IRC 客户端封装（共享）
├── ai_agent.py       # AI Agent 实现（共享）
├── start_bot2.ps1    # 悦然启动脚本
├── start_bot3.ps1    # 志远启动脚本
├── test_*.py         # 单元测试文件
├── CHANGELOG_*.md    # 功能更新日志
└── .env              # 环境变量配置
```

## 开发和测试

### 单独测试功能
```powershell
# 测试括号清理功能
uv run python test_clean_brackets.py

# 测试人类用户检测
uv run python test_user_detection.py

# 测试 Ling-1T API 连接
uv run python test_ling.py

# 测试时间注入功能
uv run python test_time_injection.py

# 测试时间感知系统
uv run python test_time_awareness.py
```

## 核心技术细节

### 时间感知对话历史管理 ⏰

为了解决 Agent "时间感错乱"问题（例如 4 小时后还在纠结午饭前的话题），系统实现了完整的时间感知机制：

#### 四大核心机制

1. **消息时间戳跟踪**
   - 每条消息记录精确的发送时间
   - 维护 `message_timestamps: dict[int, datetime]` 映射

2. **历史消息过期标记**
   - 超过 **30 分钟**的消息自动标记为 `[历史对话]`
   - AI 看到标记后会降低其权重，避免纠结过时话题

3. **自动重置机制**
   - 超过 **60 分钟**无新消息 → 自动清空历史（保留系统提示）
   - 适用于午休、下班后重新开始对话的场景

4. **动态时间注入**
   - 每次 API 调用时注入当前时间 `[当前时间：2025年10月13日 15点35分]`
   - AI 能判断话题是否过时

#### 效果对比

| 场景 | 改进前 | 改进后 |
|------|--------|--------|
| 午休后回来 | 继续纠结午饭前的话题 ❌ | 自动重置，清爽开场 ✅ |
| 长时间讨论 | 所有消息权重相同 ❌ | 旧消息降权，关注最新话题 ✅ |
| 时间跨度大 | 分不清"刚才"和"4小时前" ❌ | 明确区分历史对话 ✅ |

详细实现请参考：[CHANGELOG_TIME_AWARENESS.md](./CHANGELOG_TIME_AWARENESS.md)

### 添加新 Agent
1. 复制 `configX.py` 和 `mainX.py`（X 为数字）
2. 修改 `IRCConfig.nickname` 和 `AgentConfig.system_prompt`
3. **重要**：更新 `ai_agent.py` 中的 `KNOWN_BOTS` 列表
4. 创建对应的 `start_botX.ps1` 启动脚本

## 系统提示编写准则

在编写或修改 Agent 的 `system_prompt` 时，遵循以下关键约定：

- **严禁括号**：强调 "❌ 绝对不要用括号写旁白或舞台指示"
- **自然对话**：强调 "你是真实的聊天参与者，不是在演剧本"
- **暂停时机**：明确何时应该停止回复（如 "好的"、"谢谢" 等终止词）
- **时间感知**：不需要在提示中说明时间注入（系统自动处理）

## 常见陷阱和注意事项

1. **忘记更新 KNOWN_BOTS**：添加新 Agent 后必须在 `ai_agent.py` 中更新列表，否则会被识别为人类
2. **大小写敏感**：用户名比较使用 `.lower()`，但配置文件中的昵称本身区分大小写
3. **API 配置混淆**：志远使用 `LING_API_KEY`，其他两个用 `OPENAI_API_KEY`
4. **强制退出**：使用 `os._exit(0)` 强制退出，因为 miniirc 的线程可能阻塞普通退出
5. **括号清理过激**：如果 AI 需要在回复中使用括号（如数学表达式），需要修改 `remove_parenthetical_content()`

## 技术要求

- **Python**：>= 3.13
- **包管理器**：推荐使用 `uv`
- **核心依赖**：
  - `openai`：OpenAI SDK（兼容 Ling API）
  - `miniirc`：轻量级 IRC 客户端库
  - `python-dotenv`：环境变量加载

## 未来扩展方向

- [ ] 向量数据库集成（长期记忆，语义检索）
- [ ] 话题边界检测（自动分段记忆）
- [ ] 用户级记忆（为每个用户维护长期记忆）
- [ ] 任务分配和跟踪系统
- [ ] 多频道支持
- [ ] Web 监控界面
- [ ] 命令系统（如 `!reset`、`!status`）
- [ ] 日志和对话记录持久化
- [ ] 话题摘要机制（压缩旧对话）

## 更新日志

- **2025-10-13**：实现时间感知对话历史管理（时间戳跟踪、自动重置、历史标记）
- **2025-XX-XX**：添加人类用户检测机制
- **2025-XX-XX**：实现动态时间注入功能
- **2025-XX-XX**：添加括号清理系统

## License

MIT
