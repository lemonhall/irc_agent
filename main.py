"""主程序入口"""
import logging
from config import IRCConfig, OpenAIConfig, AgentConfig
from irc_client import IRCClient
from ai_agent import AIAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    # 加载配置
    irc_config = IRCConfig()
    openai_config = OpenAIConfig()
    agent_config = AgentConfig()
    
    # 检查 API Key
    if not openai_config.api_key:
        logger.error("请设置 OPENAI_API_KEY 环境变量")
        return
    
    logger.info("=== IRC AI Agent 启动 ===")
    logger.info(f"IRC 服务器: {irc_config.server}:{irc_config.port}")
    logger.info(f"频道: {irc_config.channel}")
    logger.info(f"昵称: {irc_config.nickname}")
    logger.info(f"API Base URL: {openai_config.base_url}")
    logger.info(f"AI 模型: {openai_config.model}")
    
    # 创建 AI Agent
    agent = AIAgent(openai_config, agent_config)
    
    # 创建 IRC 客户端
    irc_client = IRCClient(
        server=irc_config.server,
        port=irc_config.port,
        nickname=irc_config.nickname,
        channels=[irc_config.channel],
        use_ssl=irc_config.use_ssl,
        sasl_username=irc_config.sasl_username,
        sasl_password=irc_config.sasl_password
    )
    
    # 注册消息处理器
    def handle_message(channel: str, sender: str, message: str):
        """处理 IRC 消息"""
        # 判断是否需要回复
        if agent.should_respond(message, sender, irc_config.nickname):
            logger.info(f"触发回复条件: {sender}: {message}")
            
            # 生成回复
            response = agent.generate_response(channel, sender, message)
            
            # 发送回复（不添加前缀，让 AI 自己决定如何回复）
            irc_client.send_message(channel, response)
    
    irc_client.on_message(handle_message)
    
    # 连接到 IRC（这会阻塞）
    try:
        irc_client.connect()
    except KeyboardInterrupt:
        logger.info("程序退出")


if __name__ == "__main__":
    main()
