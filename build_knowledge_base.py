import os
import re

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


# ==================================================
# 1. 加载环境变量
# ==================================================

load_dotenv()

API_KEY = os.getenv("QWEN_API_KEY")


# ==================================================
# 2. 创建千问客户端
# ==================================================

client = OpenAI(
    api_key=API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# ==================================================
# 3. 创建 ChromaDB 客户端
# ==================================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)


# ==================================================
# 4. 构建企业知识库
# ==================================================

def build_knowledge_base():
    print("\n======================================")
    print("开始构建企业知识库")
    print("======================================")

    # --------------------------------------------------
    # 检查 API Key
    # --------------------------------------------------

    if not API_KEY:
        raise ValueError(
            "未检测到 QWEN_API_KEY，请检查环境变量配置。"
        )

    # --------------------------------------------------
    # PDF 路径
    # --------------------------------------------------

    pdf_path = "./documents/差旅报销管理制度.pdf"

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"找不到知识库 PDF：{pdf_path}"
        )

    # --------------------------------------------------
    # 删除旧知识库
    # --------------------------------------------------

    try:
        chroma_client.delete_collection(
            name="company_knowledge"
        )
        print("旧知识库已删除。")
    except Exception:
        print("没有找到旧知识库，直接创建新知识库。")

    # --------------------------------------------------
    # 创建新知识库
    # --------------------------------------------------

    collection = chroma_client.create_collection(
        name="company_knowledge"
    )

    # --------------------------------------------------
    # 读取 PDF
    # --------------------------------------------------

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    print("PDF读取成功！")

    # --------------------------------------------------
    # 清理文本
    # --------------------------------------------------

    text = text.replace("\u00a0", " ")
    text = re.sub(r"\n+", "\n", text)

    # --------------------------------------------------
    # 按「第X条」切分 Chunk
    # --------------------------------------------------

    chunks = re.split(
        r"(?=第[一二三四五六七八九十百千万]+条)",
        text
    )

    chunks = [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]

    print(f"Chunk数量：{len(chunks)}")

    # --------------------------------------------------
    # Chunk ID
    # --------------------------------------------------

    ids = [
        f"chunk_{i + 1:03d}"
        for i in range(len(chunks))
    ]

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    metadatas = []
    current_chapter = "总则"

    for chunk in chunks:

        # 提取章节
        chapter_match = re.search(
            r"(第[一二三四五六七八九十百千万]+章\s+[^\n]+)",
            chunk
        )

        if chapter_match:
            current_chapter = chapter_match.group(1)

        # 提取条款编号
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

        metadatas.append({
            "source": "差旅报销管理制度.pdf",
            "chapter": current_chapter,
            "section": section,
            "title": title
        })

    # --------------------------------------------------
    # 生成 Embedding
    # --------------------------------------------------

    print("正在生成 Embedding，请稍候……")

    BATCH_SIZE = 10
    embeddings = []

    for i in range(0, len(chunks), BATCH_SIZE):

        batch = chunks[i:i + BATCH_SIZE]

        print(
            f"正在处理第 {i + 1} - "
            f"{i + len(batch)} 个 Chunk..."
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

    # --------------------------------------------------
    # 保存到 ChromaDB
    # --------------------------------------------------

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("\n知识库构建完成！")
    print("当前文档数量：", collection.count())
    print("向量维度：", len(embeddings[0]))

    print("======================================")
    print("企业知识库初始化完成")
    print("======================================\n")

    return True


# ==================================================
# 5. 判断知识库是否存在
# ==================================================

def knowledge_base_exists():
    try:
        collection = chroma_client.get_collection(
            name="company_knowledge"
        )

        return collection.count() > 0

    except Exception:
        return False


# ==================================================
# 6. 本地直接运行
# ==================================================

if __name__ == "__main__":
    build_knowledge_base()
