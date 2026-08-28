import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI


# ==================================================
# 1. 读取环境变量
# ==================================================

load_dotenv()

API_KEY = os.getenv("QWEN_API_KEY")


# ==================================================
# 2. 创建阿里云百炼客户端
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
# 4. Lazy Load 知识库
# ==================================================

def get_collection():
    """
    延迟加载企业知识库。

    不在模块 import 时直接获取 Collection，
    避免 Render 部署启动时知识库尚未初始化，
    导致：

        Collection [company_knowledge] does not exist

    """

    try:

        return chroma_client.get_collection(
            name="company_knowledge"
        )

    except Exception as e:

        raise RuntimeError(
            "企业知识库不存在，请先完成知识库初始化。"
            f"原始错误：{str(e)}"
        )


# ==================================================
# 5. RAG 参数
# ==================================================

# 如果最相关结果的 Distance 太大，
# 说明用户问题可能与知识库无关。
#
# Distance 越小，通常表示向量越相似。

DISTANCE_THRESHOLD = 1.0


# ==================================================
# 6. 相对相关性范围
# ==================================================

RELATIVE_DISTANCE_MARGIN = 0.20


# ==================================================
# 7. Top-K
# ==================================================

TOP_K = 5


# ==================================================
# 8. 知识库检索函数
# ==================================================

def search_knowledge(question):
    """
    根据用户问题，从企业知识库中检索相关内容。

    返回：

    found
        是否找到相关知识

    context
        最终提供给 LLM 的知识内容

    sources
        最终使用的知识来源
    """

    print("\n==============================")
    print("RAG 开始检索")
    print("==============================")

    print(
        "检索问题：",
        question
    )


    # ==================================================
    # 8.1 获取知识库
    # ==================================================

    print(
        "正在加载企业知识库..."
    )

    collection = get_collection()

    print(
        "企业知识库加载成功。"
    )


    # ==================================================
    # 8.2 将用户问题转换成向量
    # ==================================================

    print(
        "① 正在生成 Query Embedding..."
    )

    embedding_response = client.embeddings.create(
        model="text-embedding-v4",
        input=question
    )

    question_embedding = (
        embedding_response.data[0].embedding
    )

    print(
        "① Query Embedding 生成完成"
    )


    # ==================================================
    # 8.3 从 ChromaDB 检索 Top-K
    # ==================================================

    print(
        f"② 正在检索 Top {TOP_K}..."
    )

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=TOP_K,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    print(
        "② 检索完成"
    )


    # ==================================================
    # 8.4 获取检索结果
    # ==================================================

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]


    # ==================================================
    # 防御性检查
    # ==================================================

    if not documents:

        print(
            "知识库没有返回任何结果。"
        )

        return {
            "found": False,
            "context": "",
            "sources": []
        }


    # ==================================================
    # 8.5 打印 Top-K 结果
    # ==================================================

    print(
        "\n检索结果："
    )

    for i, (
        document,
        metadata,
        distance
    ) in enumerate(
        zip(
            documents,
            metadatas,
            distances
        ),
        start=1
    ):

        print(
            f"\n--- Result {i} ---"
        )

        print(
            "来源：",
            metadata.get("source")
        )

        print(
            "章节：",
            metadata.get("chapter")
        )

        print(
            "条款：",
            metadata.get("section")
        )

        print(
            "标题：",
            metadata.get("title")
        )

        print(
            "Distance：",
            round(distance, 4)
        )


    # ==================================================
    # 8.6 判断最相关结果
    # ==================================================

    best_distance = distances[0]

    print(
        "\n最相关 Distance：",
        round(best_distance, 4)
    )


    if best_distance >= DISTANCE_THRESHOLD:

        print(
            f"③ 最相关结果 Distance >= "
            f"{DISTANCE_THRESHOLD}"
        )

        print(
            "判定：知识库中没有找到相关内容"
        )

        print(
            "================================\n"
        )

        return {
            "found": False,
            "context": "",
            "sources": []
        }


    # ==================================================
    # 8.7 根据相对相关性进行过滤
    # ==================================================

    filtered_documents = []

    sources = []

    max_allowed_distance = (
        best_distance
        + RELATIVE_DISTANCE_MARGIN
    )


    print(
        "\n③ 开始进行相对相关性过滤"
    )

    print(
        "最佳 Distance：",
        round(
            best_distance,
            4
        )
    )

    print(
        "允许的最大 Distance：",
        round(
            max_allowed_distance,
            4
        )
    )


    # ==================================================
    # 8.8 遍历 Top-K
    # ==================================================

    for (
        document,
        metadata,
        distance
    ) in zip(
        documents,
        metadatas,
        distances
    ):

        if distance <= max_allowed_distance:

            print(
                "✓ 保留：",
                metadata.get("section"),
                "Distance:",
                round(
                    distance,
                    4
                )
            )

            filtered_documents.append(
                document
            )

            sources.append({

                "source":
                    metadata.get("source"),

                "chapter":
                    metadata.get("chapter"),

                "section":
                    metadata.get("section"),

                "title":
                    metadata.get("title"),

                "distance":
                    distance

            })

        else:

            print(
                "✗ 过滤：",
                metadata.get("section"),
                "Distance:",
                round(
                    distance,
                    4
                )
            )


    # ==================================================
    # 8.9 判断过滤结果
    # ==================================================

    if not filtered_documents:

        print(
            "\n④ 没有任何 Chunk "
            "通过相关性过滤"
        )

        print(
            "================================\n"
        )

        return {
            "found": False,
            "context": "",
            "sources": []
        }


    # ==================================================
    # 8.10 构建最终 Context
    # ==================================================

    context = "\n\n".join(
        filtered_documents
    )


    print(
        "\n④ 最终进入 Context 的 Chunk 数量：",
        len(filtered_documents)
    )

    print(
        "\n=============================="
    )

    print(
        "RAG 检索完成"
    )

    print(
        "==============================\n"
    )


    # ==================================================
    # 8.11 返回 RAG 结果
    # ==================================================

    return {

        "found":
            True,

        "context":
            context,

        "sources":
            sources

    }