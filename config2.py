"""第二个 AI Agent - 配置文件"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class IRCConfig:
    """IRC 连接配置"""
    server: str = os.getenv("IRC_SERVER", "irc.lemonhall.me")
    port: int = int(os.getenv("IRC_PORT", "6667"))
    nickname: str = "yueran"  # 悦然 - 活泼型参与者
    channel: str = os.getenv("IRC_CHANNEL", "ai-collab-test")
    use_ssl: bool = os.getenv("IRC_USE_SSL", "false").lower() == "true"
    # SASL 认证（如果需要）
    sasl_username: str = os.getenv("IRC_SASL_USERNAME", "")
    sasl_password: str = os.getenv("IRC_SASL_PASSWORD", "")


@dataclass
class OpenAIConfig:
    """OpenAI API 配置"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_tokens: int = 500
    temperature: float = 0.8  # 比第一个 bot 更有创造性


@dataclass
class AgentConfig:
    """Agent 行为配置"""
    # 触发关键词
    trigger_on_mention: bool = True
    trigger_keywords: list[str] = None
    # 系统提示 - 给第二个 bot 不同的性格
    system_prompt: str = """你是 IRC 聊天室的参与者悦然（yueran），风格活泼有趣，喜欢用新颖的角度看问题。

【风格】轻松幽默，善用比喻和emoji😊，2-3句话，直接说话（不要用任何身份前缀）

【主动回应】
- 明轩或其他人的观点很有趣，你有不同角度
- 有讨论话题或气氛需要活跃
- 可以礼貌地和明轩探讨

【等待时机】
- 对方说"总结"、"好的"、"明白"、"谢谢" → 停止，等新话题  
- 明轩刚回复专业内容 → 让其他人消化，别急着接
- 连续3轮以上对话 → 暂停，给其他人留空间

可以用 "@明轩 不过呢～" 或直接称呼对方来自然对话。记住：你只是一个聊天室的普通参与者。"""

    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = ["help", "帮助", "协作", "讨论"]
