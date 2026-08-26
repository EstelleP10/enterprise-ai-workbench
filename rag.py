import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI


# ==============================
# 1. 读取 .env
# ==============================

load_dotenv()


# ==============================
# 2. 创建阿里云百炼客户端
# ==============================

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# ==============================
# 3. 连接 ChromaDB
# ==============================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)


# ==============================
# 4. 获取知识库
# ==============================

collection = chroma_client.get_collection(
    name="company_knowledge"
)


# ==============================
# 5. RAG 参数
# ==============================

# 如果最相关结果的 Distance 太大，
# 说明用户问题可能与知识库无关。
#
# Distance 越小，通常表示向量越相似。
DISTANCE_THRESHOLD = 1.0


# 相对相关性范围。
#
# 不再使用固定的：
#
# Distance < 0.50
#
# 而是以最相关结果为基准，
# 允许其他结果比最佳结果稍微差一些。
#
# 例如：
#
# Best Distance = 0.45
# Margin = 0.20
#
# 最大允许 Distance：
# 0.45 + 0.20 = 0.65
#
# 那么 0.53 的结果仍然可以进入 Context。
RELATIVE_DISTANCE_MARGIN = 0.20


# 一次最多检索多少个 Chunk。
TOP_K = 5


# ==============================
# 6. 知识库检索函数
# ==============================

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


    # ==============================
    # 6.1 将用户问题转换成向量
    # ==============================

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


    # ==============================
    # 6.2 从 ChromaDB 检索 Top-K
    # ==============================

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


    # ==============================
    # 6.3 获取检索结果
    # ==============================

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]


    print(
        "② 检索完成"
    )


    print(
        "\n检索结果："
    )


    # ==============================
    # 6.4 打印所有 Top-K 结果
    # ==============================

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


    # ==============================
    # 6.5 判断最相关结果
    # ==============================

    best_distance = distances[0]


    print(
        "\n最相关 Distance：",
        round(best_distance, 4)
    )


    # 如果最相关结果都非常不相关，
    # 则认为知识库没有找到有效内容。

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


    # ==============================
    # 6.6 根据相对相关性进行过滤
    # ==============================

    filtered_documents = []

    sources = []


    # 最相关结果作为基准。
    #
    # 例如：
    #
    # Best Distance = 0.45
    #
    # 那么允许的最大 Distance：
    #
    # 0.45 + 0.20 = 0.65

    max_allowed_distance = (
        best_distance
        + RELATIVE_DISTANCE_MARGIN
    )


    print(
        "\n③ 开始进行相对相关性过滤"
    )


    print(
        "最佳 Distance：",
        round(best_distance, 4)
    )


    print(
        "允许的最大 Distance：",
        round(
            max_allowed_distance,
            4
        )
    )


    # 遍历所有 Top-K 结果。

    for (
        document,
        metadata,
        distance
    ) in zip(
        documents,
        metadatas,
        distances
    ):


        # 如果当前结果距离
        # 小于等于允许的最大距离，
        # 则认为它与最佳结果足够接近。

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


    # ==============================
    # 6.7 判断过滤之后是否还有结果
    # ==============================

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


    # ==============================
    # 6.8 构建最终 Context
    # ==============================

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


    # ==============================
    # 6.9 返回 RAG 结果
    # ==============================

    return {

        "found":
            True,

        "context":
            context,

        "sources":
            sources

    }