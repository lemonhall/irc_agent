"""简易 IRC 聊天客户端"""
import miniirc
import threading
import sys
from datetime import datetime

# ANSI 颜色代码（PowerShell 和大多数终端都支持）
class Color:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # 前景色
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

# 配置
SERVER = "irc.lemonhall.me"
PORT = 6667
NICK = input("输入你的昵称 (不超过9个字符): ").strip()[:9] or "user"
CHANNEL = "#ai-collab-test"

print(f"\n{Color.CYAN}正在连接到 {SERVER}:{PORT}{Color.RESET}")
print(f"{Color.CYAN}昵称: {Color.BOLD}{NICK}{Color.RESET}")
print(f"{Color.CYAN}频道: {CHANNEL}{Color.RESET}")
print(f"{Color.GRAY}{'=' * 60}{Color.RESET}")

# 创建 IRC 客户端
irc = miniirc.IRC(
    ip=SERVER,
    port=PORT,
    nick=NICK,
    channels=[CHANNEL],
    ssl=False,
    debug=False  # 关闭调试信息
)

connected = threading.Event()
users_list = set()  # 存储频道中的用户列表

# 欢迎消息
@irc.Handler("001", colon=False)
def handle_welcome(irc, hostmask, args):
    print(f"{Color.GREEN}✓ 已连接到服务器{Color.RESET}")
    connected.set()

# 加入频道
@irc.Handler("JOIN", colon=False)
def handle_join(irc, hostmask, args):
    channel = args[0]
    user = hostmask[0]
    users_list.add(user)  # 添加用户到列表
    
    if user == NICK:
        print(f"{Color.GREEN}✓ 已加入频道: {channel}{Color.RESET}")
        print(f"{Color.GRAY}{'=' * 60}{Color.RESET}")
        print(f"{Color.YELLOW}现在可以开始聊天了！{Color.RESET}")
        print(f"{Color.GRAY}  - 直接输入消息发送到频道{Color.RESET}")
        print(f"{Color.GRAY}  - 输入 /users 查看在线用户{Color.RESET}")
        print(f"{Color.GRAY}  - 输入 /quit 退出{Color.RESET}")
        print(f"{Color.GRAY}{'=' * 60}{Color.RESET}\n")
    else:
        print(f"{Color.DIM}{Color.GRAY}>>> {user} 加入了频道{Color.RESET}")
        print(f"{Color.BOLD}{NICK}{Color.RESET}> ", end="", flush=True)

# 离开频道
@irc.Handler("PART", colon=False)
def handle_part(irc, hostmask, args):
    channel = args[0]
    user = hostmask[0]
    users_list.discard(user)  # 从用户列表中移除
    print(f"\r\033[K{Color.DIM}{Color.GRAY}<<< {user} 离开了频道{Color.RESET}")
    print(f"{Color.BOLD}{NICK}{Color.RESET}> ", end="", flush=True)

# 用户列表响应 (353 = NAMES reply)
@irc.Handler("353", colon=False)
def handle_names(irc, hostmask, args):
    # args 格式: [nick, '=', channel, 'user1 user2 user3']
    if len(args) >= 4:
        users = args[3].split()
        for user in users:
            # 移除用户模式前缀 (@, +, 等)
            clean_user = user.lstrip('@+~&')
            users_list.add(clean_user)

# 接收消息
@irc.Handler("PRIVMSG", colon=False)
def handle_message(irc, hostmask, args):
    channel = args[0]
    message = args[1]
    sender = hostmask[0]
    
    # 获取时间戳
    timestamp = datetime.now().strftime("%H:%M")
    
    # 根据发送者显示不同颜色
    if sender == NICK:
        # 自己的消息 - 不显示（已经在输入时显示了）
        return
    
    # 清除当前输入行，显示消息，然后重新显示输入提示
    print(f"\r\033[K{Color.GRAY}[{timestamp}]{Color.RESET} ", end="")
    
    if sender == "aibot":
        # Bot 消息 - 青色
        print(f"{Color.CYAN}{sender}{Color.RESET}: {message}")
    else:
        # 其他人的消息 - 绿色
        print(f"{Color.GREEN}{sender}{Color.RESET}: {message}")
    
    # 重新显示输入提示符
    print(f"{Color.BOLD}{NICK}{Color.RESET}> ", end="", flush=True)

# 错误处理
@irc.Handler("ERROR", colon=False)
def handle_error(irc, hostmask, args):
    print(f"{Color.RED}❌ 错误: {args}{Color.RESET}")

def input_thread():
    """处理用户输入的线程"""
    connected.wait()  # 等待连接成功
    
    while True:
        try:
            # 显示输入提示
            message = input(f"{Color.BOLD}{NICK}{Color.RESET}> ")
            if message.strip():
                command = message.strip().lower()
                
                if command == '/quit':
                    print(f"\n{Color.YELLOW}正在断开连接...{Color.RESET}")
                    irc.disconnect()
                    sys.exit(0)
                elif command in ['/users', '/who', '/list']:
                    # 显示在线用户列表
                    timestamp = datetime.now().strftime("%H:%M")
                    print(f"\r\033[K{Color.GRAY}[{timestamp}]{Color.RESET} {Color.CYAN}频道用户 ({len(users_list)} 人):{Color.RESET}")
                    for user in sorted(users_list):
                        if user == NICK:
                            print(f"  {Color.MAGENTA}• {user} (你){Color.RESET}")
                        elif user.startswith('aibot'):
                            print(f"  {Color.CYAN}• {user} [Bot]{Color.RESET}")
                        else:
                            print(f"  {Color.GREEN}• {user}{Color.RESET}")
                    print(f"{Color.BOLD}{NICK}{Color.RESET}> ", end="", flush=True)
                else:
                    # 发送消息
                    irc.msg(CHANNEL, message)
                    # 显示自己发送的消息（带时间戳）
                    timestamp = datetime.now().strftime("%H:%M")
                    print(f"\033[F\033[K{Color.GRAY}[{timestamp}]{Color.RESET} {Color.MAGENTA}{NICK}{Color.RESET}: {message}")
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n{Color.YELLOW}正在断开连接...{Color.RESET}")
            irc.disconnect()
            sys.exit(0)

# 启动输入线程
input_handler = threading.Thread(target=input_thread, daemon=True)
input_handler.start()

# 连接到 IRC
try:
    irc.connect()
except KeyboardInterrupt:
    print(f"\n\n{Color.YELLOW}正在断开连接...{Color.RESET}")
    irc.disconnect()
    print(f"{Color.GREEN}✓ 已断开{Color.RESET}")
