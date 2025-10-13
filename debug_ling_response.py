"""调试 Ling-1T API 响应格式"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LING_BASE_URL", "https://api.tbox.cn/api/llm/v1/"),
    api_key=os.getenv("LING_API_KEY", "")
)

print("正在调用 Ling-1T API...\n")

response = client.chat.completions.create(
    model="Ling-1T",
    messages=[
        {"role": "system", "content": "你是一个友好的助手。"},
        {"role": "user", "content": "你好，简单介绍一下自己。"}
    ]
)

print("=" * 60)
print("完整响应对象：")
print("=" * 60)
print(f"Type: {type(response)}")
print(f"\nResponse object: {response}")

print("\n" + "=" * 60)
print("Choices 属性：")
print("=" * 60)
print(f"choices type: {type(response.choices)}")
print(f"choices value: {response.choices}")

if response.choices:
    print("\n" + "=" * 60)
    print("第一个 Choice：")
    print("=" * 60)
    choice = response.choices[0]
    print(f"choice type: {type(choice)}")
    print(f"choice: {choice}")
    
    print("\n" + "=" * 60)
    print("Message 对象：")
    print("=" * 60)
    print(f"message type: {type(choice.message)}")
    print(f"message: {choice.message}")
    
    print("\n" + "=" * 60)
    print("Content：")
    print("=" * 60)
    print(f"content type: {type(choice.message.content)}")
    print(f"content value: {choice.message.content}")
else:
    print("\n⚠️  choices 为空或 None！")

print("\n" + "=" * 60)
print("完整 JSON (如果可序列化)：")
print("=" * 60)
try:
    print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"无法序列化: {e}")
