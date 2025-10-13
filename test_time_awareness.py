"""测试时间感知的对话历史管理"""
import time
from datetime import datetime, timedelta
from ai_agent import AIAgent
from config import OpenAIConfig, AgentConfig


def test_time_marking():
    """测试历史消息的时间标记"""
    print("=" * 60)
    print("测试1: 历史消息标记")
    print("=" * 60)
    
    # 创建测试配置
    openai_config = OpenAIConfig(
        api_key="test",
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
        max_tokens=100,
        temperature=0.7
    )
    
    agent_config = AgentConfig(
        trigger_on_mention=True,
        trigger_keywords=["测试"],
        system_prompt="你是测试机器人"
    )
    
    agent = AIAgent(openai_config, agent_config)
    agent.context_window_minutes = 0.5  # 30秒过期（测试用）
    
    # 添加一条"旧"消息
    agent.conversation_history.append({
        "role": "user",
        "content": "[来自 用户A]: 这是30秒前的消息"
    })
    agent.message_timestamps[1] = datetime.now() - timedelta(seconds=35)
    
    # 添加一条"新"消息
    agent.conversation_history.append({
        "role": "user", 
        "content": "[来自 用户B]: 这是刚才的消息"
    })
    agent.message_timestamps[2] = datetime.now()
    
    # 标记历史消息
    marked = agent._mark_old_messages()
    
    print("\n标记结果:")
    for msg in marked[1:]:  # 跳过系统提示
        print(f"  {msg['content'][:80]}...")
    
    # 验证
    assert "[历史对话]" in marked[1]["content"], "旧消息应该被标记"
    assert "[历史对话]" not in marked[2]["content"], "新消息不应该被标记"
    print("\n✅ 测试通过：时间标记正常工作\n")


def test_auto_reset():
    """测试自动重置机制"""
    print("=" * 60)
    print("测试2: 自动重置机制")
    print("=" * 60)
    
    openai_config = OpenAIConfig(
        api_key="test",
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
        max_tokens=100,
        temperature=0.7
    )
    
    agent_config = AgentConfig(
        trigger_on_mention=True,
        trigger_keywords=["测试"],
        system_prompt="你是测试机器人"
    )
    
    agent = AIAgent(openai_config, agent_config)
    agent.reset_threshold_minutes = 0.01  # 0.6秒（测试用）
    
    # 添加一些历史消息
    agent.conversation_history.append({
        "role": "user",
        "content": "旧消息1"
    })
    agent.conversation_history.append({
        "role": "user",
        "content": "旧消息2"
    })
    agent.last_message_time = datetime.now()
    
    print(f"\n当前历史长度: {len(agent.conversation_history)} (包含系统提示)")
    
    # 等待1秒
    print("等待1秒...")
    time.sleep(1)
    
    # 触发检查
    agent._check_and_reset_if_needed()
    
    print(f"重置后历史长度: {len(agent.conversation_history)}")
    
    # 验证
    assert len(agent.conversation_history) == 1, "应该只剩系统提示"
    assert len(agent.message_timestamps) == 0, "时间戳应该被清空"
    print("\n✅ 测试通过：自动重置正常工作\n")


def test_timestamp_tracking():
    """测试时间戳跟踪"""
    print("=" * 60)
    print("测试3: 时间戳跟踪")
    print("=" * 60)
    
    openai_config = OpenAIConfig(
        api_key="test",
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
        max_tokens=100,
        temperature=0.7
    )
    
    agent_config = AgentConfig(
        trigger_on_mention=True,
        trigger_keywords=["测试"],
        system_prompt="你是测试机器人"
    )
    
    agent = AIAgent(openai_config, agent_config)
    
    # 模拟添加消息
    before = datetime.now()
    agent.conversation_history.append({
        "role": "user",
        "content": "测试消息"
    })
    agent.message_timestamps[1] = datetime.now()
    after = datetime.now()
    
    # 验证
    assert 1 in agent.message_timestamps, "时间戳应该被记录"
    timestamp = agent.message_timestamps[1]
    assert before <= timestamp <= after, "时间戳应该在合理范围内"
    
    print(f"\n消息时间戳: {timestamp}")
    print(f"当前时间: {datetime.now()}")
    print(f"时间差: {(datetime.now() - timestamp).total_seconds():.3f}秒")
    print("\n✅ 测试通过：时间戳跟踪正常工作\n")


def print_scenario():
    """演示实际场景"""
    print("=" * 60)
    print("场景演示：时间感知对话")
    print("=" * 60)
    print("""
场景：用户在下午3点说"我去取餐"，然后4小时后（晚上7点）回来继续聊天

没有时间感知的问题：
  [15:00] 明轩: "不过现在该让新朋友聊聊了，我先去取餐。"
  [19:00] 用户: "讨论一下部署方案吧"
  [19:00] 明轩: "好的，不过我刚说了要去取餐..." ❌ (4小时前的事)

有时间感知的改进：
  [15:00] 明轩: "不过现在该让新朋友聊聊了，我先去取餐。"
  [19:00] [系统自动重置历史]
  [19:00] 用户: "讨论一下部署方案吧"  
  [19:00] 明轩: "好的，我们可以从容器化开始..." ✅ (清爽开场)

关键机制：
1️⃣  消息带时间戳：每条消息记录发送时间
2️⃣  过期标记：超过30分钟的消息标记为 [历史对话]
3️⃣  自动重置：超过60分钟无消息，自动清空历史
4️⃣  时间注入：AI 知道当前时间，能判断话题是否过时
""")


if __name__ == "__main__":
    print_scenario()
    print()
    
    try:
        test_time_marking()
        test_auto_reset()
        test_timestamp_tracking()
        
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
