from flask import Flask, request, jsonify, render_template
import os
from agent import run_agent
from build_knowledge_base import (
    build_knowledge_base,
    knowledge_base_exists
)


# ==================================================
# 创建 Flask 应用
# ==================================================

app = Flask(__name__)

# ==================================================
# 初始化企业知识库
# ==================================================

print("======================================")
print("Enterprise AI Workbench 正在启动...")
print("======================================")

try:

    if knowledge_base_exists():

        print("企业知识库已存在，直接启动。")

    else:

        print("未检测到企业知识库。")
        print("正在自动初始化知识库...")

        build_knowledge_base()

except Exception as e:

    print("企业知识库初始化失败：")
    print(e)

    raise


# ==================================================
# 简单的 Session 存储
# ==================================================

sessions = []


# ==================================================
# 首页
# ==================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ==================================================
# AI Chat API
# ==================================================

@app.route("/chat", methods=["POST"])
def chat():

    # --------------------------------------------------
    # 获取前端 JSON
    # --------------------------------------------------

    data = request.get_json(
        silent=True
    ) or {}


    # --------------------------------------------------
    # 获取用户问题
    # --------------------------------------------------

    user_input = data.get(
        "message",
        ""
    ).strip()


    # --------------------------------------------------
    # 空问题检查
    # --------------------------------------------------

    if not user_input:

        return jsonify({

            "success":
                False,

            "message":
                "请输入你的问题。"

        }), 400


    # --------------------------------------------------
    # 调用 Agent
    # --------------------------------------------------

    try:

        result = run_agent(
            user_input
        )


        # --------------------------------------------------
        # 保存 Session
        # --------------------------------------------------

        session = {

            "question":
                user_input,

            "answer":
                result.get(
                    "answer",
                    ""
                ),

            "steps":
                result.get(
                    "steps",
                    []
                ),

            "sources":
                result.get(
                    "sources",
                    []
                ),

            "duration_ms":
                result.get(
                    "total_duration_ms",
                    0
                )

        }


        sessions.insert(
            0,
            session
        )


        # --------------------------------------------------
        # 限制最近会话数量
        # --------------------------------------------------

        if len(sessions) > 20:

            sessions.pop()


        # --------------------------------------------------
        # 返回 Agent 结果
        # --------------------------------------------------

        return jsonify({

            "success":
                True,

            "answer":
                result.get(
                    "answer",
                    ""
                ),

            "steps":
                result.get(
                    "steps",
                    []
                ),

            "sources":
                result.get(
                    "sources",
                    []
                ),

            "total_duration_ms":
                result.get(
                    "total_duration_ms",
                    0
                )

        })


    except Exception as e:

        print(
            "Agent 执行错误：",
            e
        )


        return jsonify({

            "success":
                False,

            "message":
                "AI 助手暂时出现异常，请稍后重试。",

            "error":
                str(e)

        }), 500


# ==================================================
# Dashboard API
# ==================================================

@app.route(
    "/api/dashboard",
    methods=["GET"]
)
def dashboard():

    return jsonify({

        "success":
            True,

        "agent_status":
            "online",

        "knowledge_documents":
            1,

        "knowledge_chunks":
            30,

        "embedding_model":
            "text-embedding-v4",

        "vector_dimension":
            1024,

        "tools":
            3,

        "sessions":
            len(sessions)

    })


# ==================================================
# Knowledge Base API
# ==================================================

@app.route(
    "/api/knowledge",
    methods=["GET"]
)
def knowledge():

    return jsonify({

        "success":
            True,

        "documents": [

            {

                "name":
                    "差旅报销管理制度.pdf",

                "type":
                    "PDF",

                "chunks":
                    30,

                "embedding_model":
                    "text-embedding-v4",

                "vector_dimension":
                    1024,

                "status":
                    "ready"

            }

        ],

        "total_documents":
            1,

        "total_chunks":
            30

    })


# ==================================================
# Recent Sessions API
# ==================================================

@app.route(
    "/api/sessions",
    methods=["GET"]
)
def get_sessions():

    return jsonify({

        "success":
            True,

        "sessions":
            sessions

    })


# ==================================================
# Workflow API
# ==================================================

@app.route(
    "/api/workflow",
    methods=["GET"]
)
def workflow():

    return jsonify({

        "success":
            True,

        "workflow": {

            "name":
                "差旅费用智能审核",

            "status":
                "ready",

            "steps": [

                {
                    "id": 1,
                    "name": "用户提交差旅需求",
                    "status": "ready"
                },

                {
                    "id": 2,
                    "name": "AI Agent 分析需求",
                    "status": "ready"
                },

                {
                    "id": 3,
                    "name": "查询企业知识库",
                    "status": "ready"
                },

                {
                    "id": 4,
                    "name": "计算差旅费用",
                    "status": "ready"
                },

                {
                    "id": 5,
                    "name": "生成审核结果",
                    "status": "ready"
                }

            ]

        }

    })


# ==================================================
# Health Check
# ==================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "ok",

        "service":
            "Enterprise AI Workbench"

    })


# ==================================================
# 启动 Flask
# ==================================================

if __name__ == "__main__":

    print("======================================")
    print("东方智行 · Enterprise AI Workbench")
    print("======================================")
    print("访问地址：http://127.0.0.1:5001")
    print("======================================")

    port = int(os.environ.get("PORT", 5001))

    app.run(
    host="0.0.0.0",
    port=port,
    debug=False
    )