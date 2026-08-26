from flask import Flask, request, jsonify, render_template
from agent import run_agent


# ==================================================
# 创建 Flask 应用
# ==================================================

app = Flask(__name__)


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

    data = request.get_json(silent=True) or {}


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

            "success": False,

            "message": "请输入你的问题。"

        }), 400


    # --------------------------------------------------
    # 调用 Agent
    # --------------------------------------------------

    try:

        result = run_agent(
            user_input
        )


        # --------------------------------------------------
        # 返回 Agent 结果
        # --------------------------------------------------

        return jsonify({

            "success": True,

            "answer": result["answer"],

            "steps": result["steps"],

            "sources": result["sources"],

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

            "success": False,

            "message":
                "AI 助手暂时出现异常，请稍后重试。",

            "error": str(e)

        }), 500


# ==================================================
# 启动 Flask
# ==================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        "东方智行 · Enterprise AI Workbench"
    )

    print(
        "======================================"
    )

    print(
        "访问地址："
    )

    print(
        "http://127.0.0.1:5001"
    )

    print(
        "======================================"
    )


    app.run(

        host="127.0.0.1",

        port=5001,

        debug=True

    )