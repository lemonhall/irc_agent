"""OpenAI Agent 实现"""
import logging
import re
from datetime import datetime, timedelta
from openai import OpenAI
from config import OpenAIConfig, AgentConfig

logger = logging.getLogger(__name__)


def remove_parenthetical_content(text: str) -> str:
    """
    移除文本中所有括号及其内容（包括中英文括号）
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    # 移除中文括号及内容
    text = re.sub(r'[（(][^）)]*[）)]', '', text)
    # 移除可能遗漏的单个括号
    text = re.sub(r'[（(）)]', '', text)
    # 清理多余空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


class AIAgent:
    """基于 OpenAI 的 AI Agent"""
    
    import random
    
    # 已知的 bot 昵称列表
    KNOWN_BOTS = ["mingxuan", "yueran", "zhiyuan"]
    
    def __init__(self, openai_config: OpenAIConfig, agent_config: AgentConfig):
        self.openai_config = openai_config
        self.agent_config = agent_config
        self.client = OpenAI(
            api_key=openai_config.api_key,
            base_url=openai_config.base_url
        )
        # 对话历史（简单实现，可以后续优化为更复杂的记忆系统）
        self.conversation_history: list[dict] = [
            {"role": "system", "content": agent_config.system_prompt}
        ]
        self.max_history = 20  # 保留最近的对话
        
        # 时间管理相关
        self.message_timestamps: dict[int, datetime] = {}  # 消息索引 -> 时间戳
        self.last_message_time: datetime | None = None  # 最后一条消息的时间
        self.context_window_minutes = 30  # 上下文有效期（分钟）
        self.reset_threshold_minutes = 60  # 自动重置阈值（分钟）
        
        # 随机最大 bot 连续轮数（1~3）
        self.max_bot_turns = self.random.randint(1, 3)
        # 提前触发 client 初始化，避免在多线程环境中首次调用时出错
        try:
            _ = self.client.models
        except Exception:
            pass  # 忽略初始化错误
    
    def _check_and_reset_if_needed(self):
        """检查是否需要重置历史（长时间无消息）"""
        if self.last_message_time is None:
            return
        
        now = datetime.now()
        gap_minutes = (now - self.last_message_time).total_seconds() / 60
        
        if gap_minutes > self.reset_threshold_minutes:
            logger.info(f"[时间重置] {gap_minutes:.1f}分钟无消息，清空历史记录")
            self.conversation_history = [
                {"role": "system", "content": self.agent_config.system_prompt}
            ]
            self.message_timestamps.clear()
            self.last_message_time = now
    
    def _mark_old_messages(self):
        """标记过期的历史消息"""
        if not self.message_timestamps:
            return self.conversation_history
        
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=self.context_window_minutes)
        marked_history = []
        
        for idx, msg in enumerate(self.conversation_history):
            if idx == 0:  # 系统提示不标记
                marked_history.append(msg)
                continue
            
            msg_time = self.message_timestamps.get(idx)
            if msg_time and msg_time < cutoff_time:
                # 标记为历史对话
                content = msg["content"]
                if not content.startswith("[历史对话]"):
                    content = f"[历史对话] {content}"
                marked_history.append({"role": msg["role"], "content": content})
            else:
                marked_history.append(msg)
        
        return marked_history
    
    def should_respond(self, message: str, sender: str, bot_nickname: str) -> bool:
        """判断是否应该响应这条消息 - 使用 AI 智能判断"""
        # 忽略自己发送的消息
        if sender == bot_nickname:
            return False
        
        # 判断发送者是否为人类（不在已知 bot 列表中，大小写不敏感）
        is_human = sender.lower() not in [bot.lower() for bot in self.KNOWN_BOTS]
        
        message_lower = message.lower()
        
        # 0. 检查连续对话轮数 - 如果太多轮，只有被 @ 或人类发言才回复
        consecutive_bot_turns = 0
        for msg in reversed(self.conversation_history[1:]):  # 跳过系统提示
            if msg["role"] == "assistant":
                consecutive_bot_turns += 1
            else:
                # 遇到任何用户消息（包括人类和其他bot），检查是否为人类
                for bot_name in self.KNOWN_BOTS:
                    if bot_name in msg["content"]:
                        # 是 bot 消息，继续计数
                        break
                else:
                    # 是人类消息，重置最大轮数并停止计数
                    self.max_bot_turns = self.random.randint(1, 3)
                    break
        
        # 如果已经达到最大轮数，且不是人类发言，则不回复
        if consecutive_bot_turns >= self.max_bot_turns and not is_human:
            logger.info(f"已连续对话 {consecutive_bot_turns} 轮（最大{self.max_bot_turns}），暂停回复等待人类")
            return False
        
        # 1. 如果直接提及 bot 名字，必须回复
        if bot_nickname.lower() in message_lower:
            return True
        
        # 2. 对常见问候语快速响应
        greetings = [
            # 通用问候
            "大家好", "有人么", "有人吗", "在吗", "在不在",
            "hello", "hi", "hey", "anyone", "anyone here",
            "有没有人", "人呢", "都在吗",
            # 时间问候
            "早上好", "上午好", "中午好", "下午好", "晚上好", "晚安",
            "good morning", "good afternoon", "good evening", "good night",
            # 称呼问候
            "两位", "各位", "大伙", "诸位"
        ]
        for greeting in greetings:
            if greeting in message_lower:
                logger.info(f"检测到问候语，将回复: {message[:50]}...")
                return True
        
        # 3. 使用 AI 判断是否需要参与对话
        try:
            # 获取当前时间
            current_time = datetime.now()
            time_str = f"{current_time.year}年{current_time.month}月{current_time.day}日 {current_time.hour}点{current_time.minute}分"
            
            # 构建判断提示
            judge_prompt = f"""你是 IRC 聊天室的参与者。判断是否回应这条消息：

[当前时间：{time_str}]

来自 {sender}: "{message}"

✅ 应该回应：
- 有人夸你、感谢你、评价聊天内容（如"你们真逗"、"有意思"、"说得好"）
- 有提问、求助、需要意见
- 话题相关且你能补充观点
- 气氛友好，简单回应能让对话更自然

❌ 不回应：
- 纯粹的两人私聊（与你无关）
- 话题已经结束（如"好的"、"明白了"）

请只回答 "是" 或 "否"。"""

            response = self.client.chat.completions.create(
                model=self.openai_config.model,
                messages=[{"role": "user", "content": judge_prompt}],
                max_tokens=10,
                temperature=0.3  # 降低温度，使判断更确定
            )
            
            # 健壮的响应解析
            if not response or not response.choices or not response.choices[0].message:
                logger.warning(f"AI 判断返回空响应，降级到关键词触发")
                raise ValueError("Empty response from AI judge")
            
            answer = response.choices[0].message.content
            if not answer:
                logger.warning(f"AI 判断返回空内容，降级到关键词触发")
                raise ValueError("Empty content from AI judge")
                
            answer = answer.strip()
            should_reply = "是" in answer or "yes" in answer.lower()
            
            if should_reply:
                logger.info(f"AI 判断需要回复: {message[:50]}...")
            
            return should_reply
            
        except Exception as e:
            logger.error(f"AI 判断失败: {e}")
            # 如果判断失败，降级到关键词触发
            for keyword in self.agent_config.trigger_keywords:
                if keyword.lower() in message_lower:
                    return True
            return False
    
    def generate_response(self, channel: str, sender: str, message: str) -> str:
        """生成对消息的回复"""
        now = datetime.now()
        
        # 检查是否需要重置历史
        self._check_and_reset_if_needed()
        
        # 添加用户消息到历史
        user_message = f"[来自 {sender} 在 {channel}]: {message}"
        msg_index = len(self.conversation_history)
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        self.message_timestamps[msg_index] = now
        self.last_message_time = now
        
        # 保持历史长度
        if len(self.conversation_history) > self.max_history:
            # 保留系统提示和最近的消息
            old_length = len(self.conversation_history)
            self.conversation_history = [
                self.conversation_history[0]
            ] + self.conversation_history[-(self.max_history-1):]
            
            # 更新时间戳索引（移除旧消息的时间戳）
            removed_count = old_length - len(self.conversation_history)
            new_timestamps = {}
            for old_idx, timestamp in self.message_timestamps.items():
                if old_idx >= removed_count:
                    new_idx = old_idx - removed_count + 1  # +1 因为保留了系统提示
                    new_timestamps[new_idx] = timestamp
            self.message_timestamps = new_timestamps
        
        # 统计最近的连续 bot 对话轮数（从历史记录倒数）
        consecutive_bot_turns = 0
        for msg in reversed(self.conversation_history[1:]):  # 跳过系统提示
            if msg["role"] == "assistant":
                consecutive_bot_turns += 1
            else:
                # 遇到用户消息，检查是否为人类
                is_human_msg = True
                for bot_name in self.KNOWN_BOTS:
                    if bot_name in msg["content"]:
                        # 是 bot 消息
                        is_human_msg = False
                        break
                if is_human_msg:
                    # 如果遇到人类发言，停止计数
                    break
        
        # 在最后一条消息中添加对话轮数提示
        context_note = f"\n\n[系统提示：这是最近第 {consecutive_bot_turns + 1} 轮 bot 连续对话。如果已经3轮以上，应该暂停让人类参与]"
        self.conversation_history[-1]["content"] += context_note
        
        # 更新系统提示，添加当前时间信息
        current_time = datetime.now()
        time_info = f"\n\n[当前时间：{current_time.year}年{current_time.month}月{current_time.day}日 {current_time.hour}点{current_time.minute}分]"
        
        # 创建包含时间信息和历史标记的消息列表
        marked_history = self._mark_old_messages()
        messages_with_time = marked_history.copy()
        messages_with_time[0] = {
            "role": "system",
            "content": self.agent_config.system_prompt + time_info
        }
        
        try:
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_config.model,
                messages=messages_with_time,  # 使用包含时间信息和历史标记的消息列表
                max_tokens=self.openai_config.max_tokens,
                temperature=self.openai_config.temperature
            )
            
            # 健壮的响应解析
            if not response or not response.choices:
                logger.error(f"API 返回了空响应: {response}")
                return "抱歉，我没有收到有效的响应。"
            
            choice = response.choices[0]
            if not choice or not choice.message:
                logger.error(f"API 返回的 choice 无效: {choice}")
                return "抱歉，响应格式异常。"
            
            assistant_message = choice.message.content
            if not assistant_message:
                logger.error(f"API 返回的 content 为空")
                return "抱歉，我暂时无话可说。"
            
            # 清理括号内容（防止 AI 添加舞台指示或元评论）
            cleaned_message = remove_parenthetical_content(assistant_message)
            
            # 如果清理后为空，使用原消息但记录警告
            if not cleaned_message:
                logger.warning(f"清理括号后消息为空，使用原消息: {assistant_message}")
                cleaned_message = assistant_message
            elif cleaned_message != assistant_message:
                logger.info(f"已清理括号内容: {assistant_message[:100]}... -> {cleaned_message[:100]}...")
            
            # 添加助手回复到历史（使用清理后的消息）
            assistant_index = len(self.conversation_history)
            self.conversation_history.append({
                "role": "assistant",
                "content": cleaned_message
            })
            self.message_timestamps[assistant_index] = now
            
            logger.info(f"生成回复: {cleaned_message}")
            return cleaned_message
            
        except Exception as e:
            logger.error(f"调用 OpenAI API 失败: {e}", exc_info=True)
            return f"抱歉，我遇到了一些问题: {str(e)}"
    
    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history = [
            {"role": "system", "content": self.agent_config.system_prompt}
        ]
        self.message_timestamps.clear()
        self.last_message_time = None
        logger.info("对话历史已重置")
