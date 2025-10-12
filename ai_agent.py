"""OpenAI Agent 实现"""
import logging
from openai import OpenAI
from config import OpenAIConfig, AgentConfig

logger = logging.getLogger(__name__)


class AIAgent:
    """基于 OpenAI 的 AI Agent"""
    
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
        
        # 提前触发 client 初始化，避免在多线程环境中首次调用时出错
        try:
            _ = self.client.models
        except Exception:
            pass  # 忽略初始化错误
    
    def should_respond(self, message: str, sender: str, bot_nickname: str) -> bool:
        """判断是否应该响应这条消息 - 使用 AI 智能判断"""
        # 忽略自己发送的消息
        if sender == bot_nickname:
            return False
        
        message_lower = message.lower()
        
        # 0. 检查连续对话轮数 - 如果太多轮，只有被 @ 或人类发言才回复
        consecutive_bot_turns = 0
        for msg in reversed(self.conversation_history[1:]):  # 跳过系统提示
            if msg["role"] == "assistant":
                consecutive_bot_turns += 1
            elif msg["role"] == "user" and "lemonhall" in msg["content"]:
                break
        
        # 如果已经连续3轮以上，且不是人类发言，则不回复
        if consecutive_bot_turns >= 3 and sender != "lemonhall":
            logger.info(f"已连续对话 {consecutive_bot_turns} 轮，暂停回复等待人类")
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
            # 构建判断提示
            judge_prompt = f"""你是 IRC 聊天室的参与者。判断是否回应这条消息：

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
            
            answer = response.choices[0].message.content.strip()
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
        # 添加用户消息到历史
        user_message = f"[来自 {sender} 在 {channel}]: {message}"
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 保持历史长度
        if len(self.conversation_history) > self.max_history:
            # 保留系统提示和最近的消息
            self.conversation_history = [
                self.conversation_history[0]
            ] + self.conversation_history[-(self.max_history-1):]
        
        # 统计最近的连续 bot 对话轮数（从历史记录倒数）
        consecutive_bot_turns = 0
        for msg in reversed(self.conversation_history[1:]):  # 跳过系统提示
            if msg["role"] == "assistant":
                consecutive_bot_turns += 1
            elif msg["role"] == "user" and "lemonhall" in msg["content"]:
                # 如果遇到人类发言，重置计数
                break
        
        # 在最后一条消息中添加对话轮数提示
        context_note = f"\n\n[系统提示：这是最近第 {consecutive_bot_turns + 1} 轮 bot 连续对话。如果已经3轮以上，应该暂停让人类参与]"
        self.conversation_history[-1]["content"] += context_note
        
        try:
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_config.model,
                messages=self.conversation_history,
                max_tokens=self.openai_config.max_tokens,
                temperature=self.openai_config.temperature
            )
            
            assistant_message = response.choices[0].message.content
            
            # 添加助手回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            logger.info(f"生成回复: {assistant_message}")
            return assistant_message
            
        except Exception as e:
            logger.error(f"调用 OpenAI API 失败: {e}", exc_info=True)
            return f"抱歉，我遇到了一些问题: {str(e)}"
    
    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history = [
            {"role": "system", "content": self.agent_config.system_prompt}
        ]
        logger.info("对话历史已重置")
