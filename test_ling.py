from openai import OpenAI
client = OpenAI(
  base_url="https://api.tbox.cn/api/llm/v1/",
  api_key="sk-1dc33e3fadd648079be45d07c9a05093"
)

completion = client.chat.completions.create(
  model="Ling-1T",
  messages=[
    {"role": "user", "content": "你好!"}
  ]
)

print(completion.choices[0].message)