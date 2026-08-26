import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI


# 读取 .env 文件
load_dotenv()


# 创建阿里云百炼客户端
client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# 连接已经存在的 ChromaDB
chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)


# 获取知识库
collection = chroma_client.get_collection(
    name="company_knowledge"
)


# 用户的问题
question = "出差住宿有什么标准？"


# 将用户问题转换成向量
response = client.embeddings.create(
    model="text-embedding-v4",
    input=question
)


# 获取问题向量
question_embedding = response.data[0].embedding


# 在 ChromaDB 中进行相似度检索
results = collection.query(
    query_embeddings=[question_embedding],
    n_results=2
)


# 输出检索结果
print("用户问题：")
print(question)

print("\n最相关的 Chunk：")

for i, document in enumerate(results["documents"][0], start=1):
    print(f"\n--- Result {i} ---")
    print(document)