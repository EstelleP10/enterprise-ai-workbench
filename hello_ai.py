import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

question = input("请输入你的问题：")

response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "user", "content": question}
    ]
)

print("\nAI回答：")
print(response.choices[0].message.content)