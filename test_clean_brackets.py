"""测试括号清理功能"""
import re

def remove_parenthetical_content(text: str) -> str:
    """移除文本中所有括号及其内容（包括中英文括号）"""
    # 移除中文括号及内容
    text = re.sub(r'[（(][^）)]*[）)]', '', text)
    # 移除可能遗漏的单个括号
    text = re.sub(r'[（(）)]', '', text)
    # 清理多余空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# 测试用例
test_cases = [
    "串雨滴成风铃？说白了就是捕捉偶然里的必然节奏——材料是碎散的，悬挂的次序才是灵魂。（注：当前为第2轮对话，未达暂停阈值）",
    "暴雨冲刷后的土壤更肥沃，但种子破土需要的是持续的温度而非骤变的天气。真正的生态平衡或许在于：让表达成为光合作用，让沉默成为根系生长。（注：延续植物隐喻）",
    "说白了就是节奏把控，该出手时才出手。",
    "这是正常的话（这里有括号）继续说话",
    "(开头就是括号) 后面才是正文",
    "正文内容 (English parentheses) 继续",
]

print("=" * 80)
print("括号清理功能测试")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    cleaned = remove_parenthetical_content(test)
    print(f"\n测试 {i}:")
    print(f"原文: {test}")
    print(f"清理后: {cleaned}")
    print(f"是否修改: {'是' if cleaned != test else '否'}")
