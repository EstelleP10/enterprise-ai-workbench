import os
import re

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


# 读取 .env
load_dotenv()


# 创建阿里云百炼客户端
client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# 创建 ChromaDB
chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)


# 如果知识库已经存在，先删除旧知识库
try:
    chroma_client.delete_collection(
        name="company_knowledge"
    )
    print("旧知识库已删除。")
except Exception:
    print("没有找到旧知识库，直接创建新知识库。")


# 创建全新的知识库
collection = chroma_client.create_collection(
    name="company_knowledge"
)


# PDF 文件路径
pdf_path = "./documents/差旅报销管理制度.pdf"


# 读取 PDF
reader = PdfReader(pdf_path)


# 提取所有页面文本
text = ""

for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        text += page_text + "\n"


print("PDF读取成功！")


# 清理文本
text = text.replace("\u00a0", " ")
text = re.sub(r"\n+", "\n", text)


# 按照“第X条”进行 Chunk
chunks = re.split(
    r"(?=第[一二三四五六七八九十百千万]+条)",
    text
)


# 清理 Chunk
chunks = [
    chunk.strip()
    for chunk in chunks
    if chunk.strip()
]


print("Chunk数量：", len(chunks))


# 生成 Chunk ID
ids = [
    f"chunk_{i + 1:03d}"
    for i in range(len(chunks))
]


# 创建 Metadata
metadatas = []

current_chapter = "总则"


for chunk in chunks:

    # 尝试提取章节
    chapter_match = re.search(
        r"(第[一二三四五六七八九十百千万]+章\s+[^\n]+)",
        chunk
    )

    if chapter_match:
        current_chapter = chapter_match.group(1)

    # 提取条款号
    section_match = re.match(
        r"(第[一二三四五六七八九十百千万]+条)",
        chunk
    )

    if section_match:
        section = section_match.group(1)
    else:
        section = "制度标题"

    # 提取条款标题
    title_match = re.match(
        r"第[一二三四五六七八九十百千万]+条\s+([^\n]+)",
        chunk
    )

    if title_match:
        title = title_match.group(1)
    else:
        title = "制度标题"

    metadatas.append(
        {
            "source": "差旅报销管理制度.pdf",
            "chapter": current_chapter,
            "section": section,
            "title": title
        }
    )


# 使用 text-embedding-v4 生成向量
print("正在生成 Embedding，请稍候……")


# 每次最多处理 10 个 Chunk
BATCH_SIZE = 10


# 用来保存所有向量
embeddings = []


# 按批次处理 Chunk
for i in range(0, len(chunks), BATCH_SIZE):

    batch = chunks[i:i + BATCH_SIZE]

    print(
        f"正在处理第 {i + 1} - {i + len(batch)} 个 Chunk..."
    )

    response = client.embeddings.create(
        model="text-embedding-v4",
        input=batch
    )

    batch_embeddings = [
        item.embedding
        for item in response.data
    ]

    embeddings.extend(batch_embeddings)


# 保存到 ChromaDB
collection.upsert(
    ids=ids,
    documents=chunks,
    embeddings=embeddings,
    metadatas=metadatas
)


print("知识库构建完成！")
print("当前文档数量：", collection.count())
print("向量维度：", len(embeddings[0]))