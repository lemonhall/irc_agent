"""主程序入口"""
import logging
import threading
import time
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
    agent = AIAgent(openai_config, agent_config, irc_config.nickname)
    
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
    
    # 在单独的线程中运行 IRC 连接
    def run_irc():
        """在线程中运行 IRC 客户端"""
        try:
            irc_client.connect()
        except Exception as e:
            logger.error(f"IRC 连接错误: {e}")
    
    irc_thread = threading.Thread(target=run_irc, daemon=True)
    irc_thread.start()
    
    # 主线程保持运行，这样可以响应 Ctrl+C
    logger.info("Bot 运行中，按 Ctrl+C 退出...")
    logger.info("提示: 如果 Ctrl+C 无效，请直接关闭终端窗口")
    try:
        while True:
            time.sleep(0.1)  # 更短的睡眠时间，更快响应
    except KeyboardInterrupt:
        logger.info("\n\n收到中断信号，正在退出...")
        try:
            irc_client.disconnect()
            logger.info("✓ 已断开连接")
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")
        finally:
            import os
            os._exit(0)  # 强制退出


if __name__ == "__main__":
    main()
