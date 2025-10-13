"""测试时间+天气+新闻注入功能"""
from ai_agent import format_current_time

print("=" * 80)
print("测试完整信息注入")
print("=" * 80)

# 测试北京（明轩）
print("\n【明轩 - 北京】")
info = format_current_time(location="北京", include_news=True)
print(info)

# 测试深圳（悦然）
print("\n【悦然 - 深圳】")
info = format_current_time(location="深圳", include_news=True)
print(info)

# 测试上海（志远）
print("\n【志远 - 上海】")
info = format_current_time(location="上海", include_news=True)
print(info)

print("\n" + "=" * 80)
