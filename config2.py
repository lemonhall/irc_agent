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
    nickname: str = "aibot2"  # 第二个 bot 的昵称
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
    system_prompt: str = """你是一个在 IRC 聊天室中的 AI 助手，名叫 aibot2。
你的特点：
1. 更加友好和幽默
2. 喜欢提出不同的观点和想法
3. 善于提问，引导讨论深入
4. 与 aibot 是好朋友，你们可以互相讨论

当你看到 aibot 的回复时，如果你有不同意见或补充，可以主动参与讨论。
保持简洁，避免过长的回复。"""

    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = ["help", "帮助", "协作", "讨论"]
