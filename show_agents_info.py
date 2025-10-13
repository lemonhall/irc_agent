"""显示三个 AI Agent 的完整配置信息"""
from datetime import datetime

# 三个 Agent 的配置
agents = [
    {
        "name": "明轩 (mingxuan)",
        "model": "gpt-4o-mini (OpenAI)",
        "location": "北京",
        "personality": "专业理性型",
        "style": "简洁专业，4-5句话",
        "traits": [
            "擅长专业分析和深度思考",
            "常用生活化例子说明问题",
            "避免过度引用数据",
            "说话自然流畅"
        ],
        "temperature": 0.7,
        "config_file": "config.py",
        "main_file": "main.py"
    },
    {
        "name": "悦然 (yueran)",
        "model": "gpt-4o-mini (OpenAI)",
        "location": "深圳",
        "personality": "活泼有趣型",
        "style": "轻松幽默，2-3句话，善用emoji😊",
        "traits": [
            "喜欢用新颖的角度看问题",
            "善用比喻和emoji",
            "能活跃讨论气氛",
            "礼貌探讨不同观点"
        ],
        "temperature": 0.8,
        "config_file": "config2.py",
        "main_file": "main2.py"
    },
    {
        "name": "志远 (zhiyuan)",
        "model": "Ling-1T (TBox)",
        "location": "上海",
        "personality": "沉稳务实型",
        "style": "简洁实在，1-2句话",
        "traits": [
            "喜欢从大局看问题",
            "说话接地气，不装深沉",
            "常用平实表达",
            "能提供新思路"
        ],
        "temperature": 0.6,
        "config_file": "config3.py",
        "main_file": "main3.py"
    }
]

# 获取当前时间
current_time = datetime.now()
time_str = f"{current_time.year}年{current_time.month}月{current_time.day}日 {current_time.hour}点{current_time.minute}分"

print("=" * 80)
print("IRC AI Agent 配置总览")
print("=" * 80)
print(f"当前时间：{time_str}")
print(f"聊天频道：#ai-collab-test")
print(f"IRC 服务器：irc.lemonhall.me:6667")
print()

for i, agent in enumerate(agents, 1):
    print("=" * 80)
    print(f"Agent {i}: {agent['name']}")
    print("=" * 80)
    print(f"📍 地理位置：{agent['location']}")
    print(f"🤖 AI 模型：{agent['model']}")
    print(f"🎭 人格类型：{agent['personality']}")
    print(f"💬 说话风格：{agent['style']}")
    print(f"🌡️  Temperature: {agent['temperature']}")
    print(f"📝 配置文件：{agent['config_file']}")
    print(f"▶️  启动文件：{agent['main_file']}")
    print(f"\n✨ 人格特质：")
    for trait in agent['traits']:
        print(f"   • {trait}")
    print()

print("=" * 80)
print("地理分布")
print("=" * 80)
print("""
      🇨🇳 中国
      
   🏛️ 北京 - 明轩 (专业理性)
      |
   🏙️ 上海 - 志远 (沉稳务实)
      |
   🌆 深圳 - 悦然 (活泼有趣)
""")

print("=" * 80)
print("对话特点")
print("=" * 80)
print("""
明轩（北京）：专业分析，4-5句话，用生活化例子
悦然（深圳）：活泼幽默，2-3句话，用emoji和比喻
志远（上海）：沉稳实在，1-2句话，从大局看问题

三人组合形成互补：
• 明轩提供深度分析
• 悦然带来新颖角度
• 志远把握整体方向
""")

print("=" * 80)
print("启动命令")
print("=" * 80)
print("# 启动明轩（北京）")
print("uv run python main.py")
print()
print("# 启动悦然（深圳）")
print("uv run python main2.py")
print()
print("# 启动志远（上海）")
print(".\\start_bot3.ps1")
print("或")
print("uv run python main3.py")
print()
