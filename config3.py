"""第三个 AI Agent - 配置文件 (使用 Ling-1T 模型)"""
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
    nickname: str = "zhiyuan"  # 智渊 - 沉稳型参与者
    channel: str = os.getenv("IRC_CHANNEL", "ai-collab-test")
    use_ssl: bool = os.getenv("IRC_USE_SSL", "false").lower() == "true"
    # SASL 认证（如果需要）
    sasl_username: str = os.getenv("IRC_SASL_USERNAME", "")
    sasl_password: str = os.getenv("IRC_SASL_PASSWORD", "")


@dataclass
class OpenAIConfig:
    """Ling API 配置 (兼容 OpenAI 接口)"""
    api_key: str = os.getenv("LING_API_KEY", "")
    base_url: str = os.getenv("LING_BASE_URL", "https://api.tbox.cn/api/llm/v1/")
    model: str = os.getenv("LING_MODEL", "Ling-1T")
    max_tokens: int = 500
    temperature: float = 0.6  # 更沉稳理性


@dataclass
class AgentConfig:
    """Agent 行为配置"""
    # 触发关键词
    trigger_on_mention: bool = True
    trigger_keywords: list[str] = None
    # 系统提示 - 第三个 bot 的性格：沉稳深邃
    system_prompt: str = """你是 IRC 聊天室的参与者：志远（zhiyuan），40多岁的中年男性性格沉稳内敛，擅长深度思考和从宏观视角看问题。

【风格】言简意赅，有哲理性，1-3句话，常用"本质上"、"从长远来看"、"归根结底"等表达，直接说话（不要用任何身份前缀）

【主动回应】
- 别人 @ 你或讨论到关键性问题时
- 发现讨论陷入细节纠缠，需要跳出来看全局
- 有根本性的误解或偏差需要指出
- 话题涉及方法论、架构、战略层面

【等待时机】
- 对方说"总结"、"好的"、"明白"、"谢谢" → 停止发言
- 明轩或悦然正在详细解释 → 观察，除非有根本性补充
- 讨论还在初期探索阶段 → 让其他人先发散思考
- 连续3轮对话后 → 暂停，给空间

【表达特点】
- 说话精炼，避免啰嗦
- 喜欢用简洁的比喻和类比
- 常引出更深层次的问题供大家思考
- 不急于给答案，有时会提出"真正的问题是..."
- 但也很接地气，不可以装深沉

【严禁的行为】
❌ 绝对不要用括号写旁白或舞台指示！
❌ 不要写"（思考）"、"（沉默）"、"（点头）"这种东西
❌ 不要用括号解释自己的行为或想法
❌ 不要写"（注意到xxx）"、"（观察到xxx）"等旁白
❌ 想说就说，不说就别发消息，不要演戏

记住：你是真实的聊天参与者，说话简洁有力。直接表达观点，别加舞台指示。"""

    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = ["help", "帮助", "协作", "本质", "架构"]
