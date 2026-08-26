import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


text = "员工住宿费用按照公司规定的城市及职级标准执行。"


response = client.embeddings.create(
    model="text-embedding-v4",
    input=text
)


embedding = response.data[0].embedding


print("向量维度：", len(embedding))
print("向量前10个数字：", embedding[:10])