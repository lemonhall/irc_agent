"""测试人类用户识别逻辑"""

# 已知的 bot 列表
KNOWN_BOTS = ["mingxuan", "yueran", "zhiyuan"]

# 测试用例
test_users = [
    ("lemonhall", True, "原始人类用户"),
    ("nixiephoe", True, "新加入的人类用户"),
    ("mingxuan", False, "AI Bot 1"),
    ("yueran", False, "AI Bot 2"),
    ("zhiyuan", False, "AI Bot 3"),
    ("alice", True, "其他人类用户"),
    ("bob_123", True, "带下划线的人类用户"),
    ("MingXuan", False, "大小写不同但还是 bot（需要注意）"),
]

print("=" * 80)
print("人类用户识别测试")
print("=" * 80)
print()

for username, expected_is_human, description in test_users:
    # 简单的检查逻辑：不在 KNOWN_BOTS 列表中就是人类
    is_human = username not in KNOWN_BOTS
    
    status = "✓" if is_human == expected_is_human else "✗"
    user_type = "人类" if is_human else "Bot"
    
    print(f"{status} {username:15s} -> {user_type:6s} ({description})")
    
    if is_human != expected_is_human:
        print(f"   ⚠️  期望: {'人类' if expected_is_human else 'Bot'}, 实际: {user_type}")

print()
print("=" * 80)
print("注意事项")
print("=" * 80)
print("""
1. Bot 名称是大小写敏感的
   - "mingxuan" 会被识别为 Bot
   - "MingXuan" 不会被识别为 Bot（会被当作人类）
   
2. 解决方案：
   - 在比较时使用 username.lower() 统一转小写
   - 或者在 KNOWN_BOTS 中同时列出大小写变体

3. 推荐的修改：
   is_human = username.lower() not in [b.lower() for b in KNOWN_BOTS]
""")

print()
print("=" * 80)
print("改进后的测试（大小写不敏感）")
print("=" * 80)
print()

for username, expected_is_human, description in test_users:
    # 改进的检查逻辑：大小写不敏感
    is_human = username.lower() not in [b.lower() for b in KNOWN_BOTS]
    
    # 对于 "MingXuan"，它应该被识别为 bot
    if username == "MingXuan":
        expected_is_human = False
    
    status = "✓" if is_human == expected_is_human else "✗"
    user_type = "人类" if is_human else "Bot"
    
    print(f"{status} {username:15s} -> {user_type:6s} ({description})")
