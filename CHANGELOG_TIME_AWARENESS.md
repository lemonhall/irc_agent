# 时间感知对话历史管理 - 更新日志

## 📅 更新时间
2025年10月13日

## 🎯 问题背景
在之前的实现中，Agent 的对话历史采用简单的滑动窗口机制（只保留最近 20 条消息），导致了"时间感错乱"问题：

### 问题案例
```
[15:00] 明轩: "不过现在该让新朋友聊聊了，我先去取餐。"
... (4小时后) ...
[19:00] 用户: "讨论一下部署方案吧"
[19:00] 明轩: "好的，不过我刚说了要去取餐..." ❌
```

**根本原因**：Agent 不知道"4小时前的对话"和"刚才的对话"的区别，把过时的话题当成当前上下文。

---

## ✨ 解决方案

### 核心机制

#### 1️⃣ **消息时间戳跟踪**
- 为每条消息记录时间戳 `message_timestamps: dict[int, datetime]`
- 记录最后一条消息的时间 `last_message_time`

#### 2️⃣ **历史消息过期标记**
- 超过 **30 分钟**的消息自动标记为 `[历史对话]`
- AI 看到标记后会降低其权重，不会纠结过时话题

```python
def _mark_old_messages(self):
    """标记过期的历史消息"""
    cutoff_time = now - timedelta(minutes=30)
    for msg in history:
        if msg_time < cutoff_time:
            content = f"[历史对话] {content}"
```

#### 3️⃣ **自动重置机制**
- 超过 **60 分钟**无新消息 → 自动清空历史（保留系统提示）
- 适用于午休、下班后重新开始对话的场景

```python
def _check_and_reset_if_needed(self):
    """检查是否需要重置历史"""
    if gap_minutes > 60:
        logger.info(f"[时间重置] {gap_minutes:.1f}分钟无消息，清空历史")
        self.reset_conversation()
```

#### 4️⃣ **时间信息注入**（保留原有机制）
- 每次 API 调用时注入当前时间 `[当前时间：2025年10月13日 15点35分]`
- AI 能判断话题是否过时

---

## 🔧 技术实现

### 修改文件
- `ai_agent.py`

### 新增属性
```python
class AIAgent:
    def __init__(self, ...):
        # 时间管理相关
        self.message_timestamps: dict[int, datetime] = {}  # 消息索引 -> 时间戳
        self.last_message_time: datetime | None = None     # 最后消息时间
        self.context_window_minutes = 30                   # 上下文有效期
        self.reset_threshold_minutes = 60                  # 自动重置阈值
```

### 新增方法
```python
def _check_and_reset_if_needed(self):
    """检查并重置历史（长时间无消息）"""

def _mark_old_messages(self):
    """标记过期的历史消息"""
```

### 修改方法
```python
def generate_response(self, ...):
    # 1. 检查是否需要重置
    self._check_and_reset_if_needed()
    
    # 2. 记录时间戳
    msg_index = len(self.conversation_history)
    self.message_timestamps[msg_index] = now
    self.last_message_time = now
    
    # 3. 标记历史消息
    marked_history = self._mark_old_messages()
    messages_with_time = marked_history.copy()
    # ... 调用 API
```

---

## 🧪 测试验证

### 测试文件
- `test_time_awareness.py`

### 测试结果
```bash
✅ 测试1: 历史消息标记 - 通过
✅ 测试2: 自动重置机制 - 通过
✅ 测试3: 时间戳跟踪 - 通过
```

### 测试覆盖
1. **时间标记测试**：验证 30 秒前的消息被正确标记为 `[历史对话]`
2. **自动重置测试**：验证 60 分钟无消息后历史被清空
3. **时间戳跟踪测试**：验证每条消息的时间戳正确记录

---

## 📊 效果对比

| 场景 | 改进前 | 改进后 |
|------|--------|--------|
| **午休后回来** | 继续纠结午饭前的话题 ❌ | 自动重置，清爽开场 ✅ |
| **长时间讨论** | 所有消息权重相同 ❌ | 旧消息降权，关注最新话题 ✅ |
| **时间跨度大** | 分不清"刚才"和"4小时前" ❌ | 明确区分历史对话 ✅ |

---

## 🎯 使用建议

### 参数调优
根据实际使用场景调整阈值：

```python
# 快节奏讨论（技术会议）
agent.context_window_minutes = 15   # 15分钟即过期
agent.reset_threshold_minutes = 30  # 30分钟重置

# 慢节奏讨论（社区论坛）
agent.context_window_minutes = 60   # 1小时过期
agent.reset_threshold_minutes = 240 # 4小时重置
```

### 监控日志
观察自动重置的触发情况：
```
[时间重置] 65.3分钟无消息，清空历史记录
```

---

## 🚀 未来扩展

### 可能的增强方向

1. **话题摘要机制**
   - 超过 10 条的旧消息用 LLM 生成摘要
   - 保留语义信息但减少 token 消耗

2. **向量数据库集成**
   - 使用 ChromaDB/Faiss 存储所有历史
   - 按需检索相关对话（语义检索）

3. **话题边界检测**
   - 使用 LLM 判断话题是否切换
   - 话题切换时自动分段记忆

4. **用户级记忆**
   - 为每个用户维护独立的长期记忆
   - 记住用户的偏好和习惯

---

## 📝 向后兼容

- ✅ 完全兼容现有代码
- ✅ 不需要修改配置文件
- ✅ 不影响现有的时间注入机制
- ✅ 自动处理旧数据（没有时间戳的消息）

---

## 🙏 致谢

感谢 lemonhall 提出的关键问题：
> "4小时之前说自己去取餐了，然后到了晚上，还在聊取餐这破事儿？"

这个观察直击问题本质，推动了时间感知机制的诞生！🎉
