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


# 创建持久化的 ChromaDB
chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)


# 获取或创建知识库
collection = chroma_client.get_or_create_collection(
    name="company_knowledge"
)


# 准备知识库中的文本
documents = [
    "第一条 员工因公出差产生的交通费、住宿费及符合规定的市内交通费用可以申请报销。",
    "第二条 市内打车费用原则上应提供有效发票及行程记录。",
    "第三条 员工住宿费用按照公司规定的城市及职级标准执行。",
    "第四条 出差期间产生的餐费按照公司差旅补贴标准执行。"
]


# 给每个 Chunk 设置唯一 ID
ids = [
    "chunk_001",
    "chunk_002",
    "chunk_003",
    "chunk_004"
]


# 使用阿里云 Embedding 模型生成向量
response = client.embeddings.create(
    model="text-embedding-v4",
    input=documents
)


# 获取所有 Chunk 对应的向量
embeddings = [item.embedding for item in response.data]


# 将文本、ID和向量一起存入 ChromaDB
collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings
)


print("知识库创建成功！")
print("当前文档数量：", collection.count())
print("向量维度：", len(embeddings[0]))