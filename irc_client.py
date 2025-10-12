"""IRC 客户端封装"""
import logging
from typing import Callable
import miniirc

logger = logging.getLogger(__name__)


class IRCClient:
    """简单的 IRC 客户端封装"""
    
    @staticmethod
    def normalize_channel(channel: str) -> str:
        """确保频道名以 # 开头"""
        if not channel.startswith('#'):
            return f'#{channel}'
        return channel
    
    def __init__(self, server: str, port: int, nickname: str, channels: list[str], 
                 use_ssl: bool = False, sasl_username: str = "", sasl_password: str = ""):
        self.server = server
        self.port = port
        self.nickname = nickname
        # 规范化频道名
        self.channels = [self.normalize_channel(ch) for ch in channels]
        logger.info(f"规范化后的频道列表: {self.channels}")
        self.use_ssl = use_ssl
        
        # 消息处理回调
        self.message_handlers: list[Callable] = []
        
        # 创建 IRC 连接，支持 SASL 认证
        connect_modes = None
        if sasl_username and sasl_password:
            connect_modes = (sasl_username, sasl_password)
            logger.info(f"使用 SASL 认证: {sasl_username}")
        
        self.irc = miniirc.IRC(
            ip=server,
            port=port,
            nick=nickname,
            channels=self.channels,  # 使用规范化后的频道列表
            ssl=use_ssl,
            debug=False,
            ns_identity=connect_modes  # SASL 认证
        )
        
        # 注册连接成功处理器
        @self.irc.Handler("001", colon=False)  # RPL_WELCOME
        def handle_welcome(irc, hostmask, args):
            logger.info(f"✓ 成功连接到 IRC 服务器！")
        
        # 注册加入频道处理器
        @self.irc.Handler("JOIN", colon=False)
        def handle_join(irc, hostmask, args):
            channel = args[0]
            user = hostmask[0]
            if user == nickname:
                logger.info(f"✓ 成功加入频道: {channel}")
            else:
                logger.info(f"用户 {user} 加入了 {channel}")
        
        # 注册事件处理器
        @self.irc.Handler("PRIVMSG", colon=False)
        def handle_message(irc, hostmask, args):
            """处理接收到的消息"""
            channel = args[0]
            message = args[1]
            sender = hostmask[0]  # 提取发送者昵称
            
            logger.info(f"[{channel}] <{sender}> {message}")
            
            # 调用所有注册的消息处理器
            for handler in self.message_handlers:
                try:
                    handler(channel, sender, message)
                except Exception as e:
                    logger.error(f"消息处理器错误: {e}", exc_info=True)
    
    def on_message(self, handler: Callable):
        """注册消息处理回调函数"""
        self.message_handlers.append(handler)
    
    def send_message(self, channel: str, message: str):
        """发送消息到频道"""
        # IRC 消息通常需要分行，避免过长
        lines = message.split('\n')
        for line in lines:
            if line.strip():
                self.irc.msg(channel, line)
                logger.info(f"[{channel}] <{self.nickname}> {line}")
    
    def connect(self):
        """连接到 IRC 服务器（阻塞）"""
        logger.info(f"正在连接到 {self.server}:{self.port} 频道: {self.channels}")
        try:
            self.irc.connect()
        except KeyboardInterrupt:
            logger.info("收到中断信号，断开连接...")
            self.disconnect()
    
    def disconnect(self):
        """断开连接"""
        self.irc.disconnect()
        logger.info("已断开连接")
