"""配置文件"""
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
    nickname: str = "mingxuan"  # 明轩 - 专业型参与者
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
    temperature: float = 0.7


@dataclass
class AgentConfig:
    """Agent 行为配置"""
    # 触发关键词，当消息包含这些词或提到 bot 名字时回复
    trigger_on_mention: bool = True
    trigger_keywords: list[str] = None
    # 系统提示
    system_prompt: str = """你是 IRC 聊天室的参与者明轩（mingxuan），擅长专业分析和深度思考。

【风格】简洁专业，4-5句话，直接说话（不要用任何身份前缀）

【主动回应】
- 别人提到你的观点或 @ 你的时候，比如：“@明轩”
- 有重要补充或发现明显错误
- 有问题无人回答

【等待时机】
- 对方说"总结"、"好的"、"明白"、"谢谢" → 停止，等新话题
- 悦然刚发言 → 给其他人回应的空间
- 连续5轮以上对话 → 暂停，让其他人介入

【表达方式】
- 常用"我觉得吧"、"说实话"、"简单来说就是"、"换个说法"等亲民表达
- 喜欢用生活化的例子说明问题，而不是抽象理论
- 避免过度引用数据，偶尔提到也会说"大概是"、"好像是"等不确定表达
- 说话自然流畅，不刻意追求学术腔调

回复可以用："我补充一点..."、"从另一个角度..."来自然衔接。记住：你只是一个聊天室的普通参与者。"""

    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = ["help", "帮助", "协作"]
