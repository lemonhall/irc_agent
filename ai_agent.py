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
        
        # 1. 如果直接提及 bot 名字，必须回复
        if bot_nickname.lower() in message_lower:
            return True
        
        # 2. 使用 AI 判断是否需要参与对话
        try:
            # 构建判断提示
            judge_prompt = f"""你是一个 IRC 聊天室中的 AI 助手。请判断以下消息是否需要你参与回复。

消息来自用户 {sender}:
"{message}"

判断标准：
- 如果消息是提问、求助、需要建议或意见
- 如果消息与技术、学习、工作相关
- 如果消息看起来在等待回应
- 如果对话似乎停滞，你可以提供有价值的观点
则应该回复。

- 如果是日常闲聊、打招呼、私人对话
- 如果话题与你无关
- 如果已经有人在回复
则不需要回复。

请只回答 "是" 或 "否"，不要解释。"""

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
