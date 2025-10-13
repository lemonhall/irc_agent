"""测试时间信息添加功能"""
from datetime import datetime

# 模拟系统提示
system_prompt = """你是 IRC 聊天室的参与者明轩（mingxuan），擅长专业分析和深度思考。

【风格】简洁专业，4-5句话，直接说话（不要用任何身份前缀）"""

# 获取当前时间
current_time = datetime.now()
time_info = f"\n\n[当前时间：{current_time.year}年{current_time.month}月{current_time.day}日 {current_time.hour}点{current_time.minute}分]"

# 添加时间信息
system_prompt_with_time = system_prompt + time_info

print("=" * 80)
print("系统提示（原始）")
print("=" * 80)
print(system_prompt)

print("\n" + "=" * 80)
print("系统提示（添加时间后）")
print("=" * 80)
print(system_prompt_with_time)

print("\n" + "=" * 80)
print("时间信息")
print("=" * 80)
print(f"当前时间：{current_time.year}年{current_time.month}月{current_time.day}日 {current_time.hour}点{current_time.minute}分")
print(f"完整时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}")
