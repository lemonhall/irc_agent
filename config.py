"""配置文件"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class IRCConfig:
    """IRC 连接配置"""
    server: str = os.getenv("IRC_SERVER", "irc.libera.chat")
    port: int = int(os.getenv("IRC_PORT", "6667"))
    nickname: str = os.getenv("IRC_NICKNAME", "deepseek_agent")
    channel: str = os.getenv("IRC_CHANNEL", "#ai-collab-test")
    use_ssl: bool = os.getenv("IRC_USE_SSL", "false").lower() == "true"
    # SASL 认证（Libera.Chat 需要）
    sasl_username: str = os.getenv("IRC_SASL_USERNAME", "")
    sasl_password: str = os.getenv("IRC_SASL_PASSWORD", "")


@dataclass
class OpenAIConfig:
    """OpenAI API 配置"""
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_tokens: int = 500
    temperature: float = 0.7


@dataclass
class AgentConfig:
    """Agent 行为配置"""
    # 触发关键词，当消息包含这些词或提到 bot 名字时回复
    trigger_on_mention: bool = True
    trigger_keywords: list[str] = None
    # 系统提示
    system_prompt: str = """你是一个在 IRC 聊天室中的 AI 助手。
你的任务是：
1. 理解用户的请求和问题
2. 与聊天室中的其他人协作
3. 提供有用的建议和帮助
4. 保持友好和专业的态度

请用简洁的方式回复，避免过长的消息。"""

    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = ["help", "帮助", "协作"]
