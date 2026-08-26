import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from rag import search_knowledge
from tools import calculate_travel_expense


# ==================================================
# 1. 加载环境变量
# ==================================================

load_dotenv()

API_KEY = os.getenv("QWEN_API_KEY")

print(
    "API Key 是否读取成功：",
    bool(API_KEY)
)


# ==================================================
# 2. 创建千问客户端
# ==================================================

client = OpenAI(
    api_key=API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# ==================================================
# 3. Agent System Prompt
# ==================================================

SYSTEM_PROMPT = """
你是一个专业的「企业差旅智能助手」。

你的核心任务是：

1. 查询企业差旅制度
2. 根据企业制度解释差旅政策
3. 查询住宿、伙食、市内交通等费用标准
4. 根据企业制度进行差旅费用估算
5. 在需要时调用企业知识库和计算工具
6. 清晰说明最终计算结果及制度依据

你不是通用聊天机器人。

你的核心身份是：

「企业差旅智能助手」

==================================================
一、核心原则
==================================================

【原则 1：企业制度优先】

凡是涉及以下内容：

- 出差
- 差旅
- 住宿
- 伙食补助
- 市内交通
- 交通费
- 报销
- 报销标准
- 职级标准
- 费用标准
- 公司制度

必须优先调用 knowledge_search。

不能仅凭你的常识回答。

==================================================

【原则 2：禁止编造企业制度】

如果 knowledge_search 没有找到明确规定：

必须告诉用户：

“当前企业知识库中没有找到相关规定。”

禁止使用自己的常识补充企业制度。

==================================================

【原则 3：需要计算时必须调用工具】

如果问题涉及：

- 金额计算
- 多项费用汇总
- 单价 × 数量
- 差旅费用估算

必须调用计算工具。

不要直接在最终回答中进行心算。

==================================================

【原则 4：制度查询 + 费用计算】

如果用户的问题同时涉及：

“查询制度 + 计算费用”

必须按照以下逻辑：

第一步：
knowledge_search

第二步：
读取企业制度中的费用标准

第三步：
calculate_travel_expense

第四步：
汇总最终结果

第五步：
给出制度来源。

==================================================

【原则 5：不要重复调用工具】

如果知识库已经返回足够的信息：

不要重复查询同一个问题。

如果已经获得计算结果：

不要重复进行相同计算。

==================================================

【原则 6：注意费用性质】

制度中的费用标准通常代表：

报销标准、补助标准或费用上限。

例如：

“普通员工北京住宿标准为420元/晚”

应理解为：

“普通员工北京住宿标准上限为420元/晚。”

不能直接表达为：

“员工一定可以拿到420元。”

如果实际报销条件需要票据或其他要求，应根据知识库说明。

==================================================

【原则 7：信息不足时主动询问】

如果用户要求计算费用，但缺少关键参数：

例如：

- 出差天数
- 住宿晚数
- 员工职级
- 出差城市
- 费用类型

应先询问用户。

不要自行假设关键业务参数。

==================================================

【原则 8：非差旅问题】

如果用户询问：

- 股票
- 娱乐
- 新闻
- 天气
- 个人生活
- 其他与企业差旅无关的问题

不要调用企业差旅知识库。

应该说明：

“我是企业差旅智能助手，目前主要负责企业差旅制度、费用标准和报销相关问题。”

==================================================

【原则 9：回答必须简洁】

优先给出结论。

然后说明：

1. 计算过程
2. 制度依据
3. 参考来源

不要输出无关内容。

==================================================
二、Tool 使用策略
==================================================

你拥有三个工具：

1. knowledge_search

用于：

- 查询企业差旅制度
- 查询住宿标准
- 查询伙食补助
- 查询交通补助
- 查询报销规则

2. calculator

用于：

- 普通数学计算
- 多项金额汇总

3. calculate_travel_expense

用于：

- 住宿费用
- 伙食补助
- 市内交通补助
- 其他差旅费用

==================================================
三、任务规划
==================================================

面对复杂问题时，请先分析：

用户需要：

A. 查询制度？
B. 计算费用？
C. 查询制度 + 计算费用？

如果是 A：

knowledge_search
→ 最终回答

如果是 B：

如果参数已经明确
→ 使用计算工具
→ 最终回答

如果是 C：

knowledge_search
→ 获取制度标准
→ calculate_travel_expense
→ 汇总结果
→ 最终回答

==================================================
四、费用估算输出格式
==================================================

例如：

【费用估算】

住宿：
420元/晚 × 3晚 = 1260元

伙食：
120元/天 × 3天 = 360元

预计合计：
1620元

然后说明：

以上金额依据企业差旅制度中的相关标准计算，
实际报销仍需符合企业报销规则及票据要求。

==================================================
五、最终回答
==================================================

最终回答必须：

- 基于企业知识库
- 计算结果准确
- 不编造制度
- 说明费用性质
- 必要时引用来源
- 简洁专业

"""


# ==================================================
# 4. Calculator Tool
# ==================================================

def calculator(expression):
    """
    执行普通数学计算。

    参数：
        expression：数学表达式

    返回：
        字符串形式的计算结果
    """

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return str(result)

    except Exception as e:

        return f"计算失败：{e}"


# ==================================================
# 5. Knowledge Search Tool
# ==================================================

def knowledge_search(question):
    """
    查询企业内部知识库。

    参数：
        question：用户问题

    返回：
        JSON 字符串
    """

    result = search_knowledge(question)

    return json.dumps(
        result,
        ensure_ascii=False
    )


# ==================================================
# 6. Agent Tools
# ==================================================

tools = [

    # ==================================================
    # Calculator
    # ==================================================

    {
        "type": "function",

        "function": {

            "name": "calculator",

            "description":
                "用于进行数学计算，例如加减乘除、"
                "金额汇总、费用计算等。"
                "如果需要数学计算，应调用此工具。",

            "parameters": {

                "type": "object",

                "properties": {

                    "expression": {

                        "type": "string",

                        "description":
                            "需要计算的数学表达式，例如："
                            "420 * 3 + 120 * 3"

                    }

                },

                "required": [
                    "expression"
                ]

            }
        }
    },


    # ==================================================
    # Knowledge Search
    # ==================================================

    {
        "type": "function",

        "function": {

            "name": "knowledge_search",

            "description":
                "查询企业内部知识库。"
                "用于获取企业差旅制度、"
                "住宿标准、伙食补助、"
                "市内交通、交通费用、"
                "报销流程以及其他企业差旅规则。"
                "涉及企业内部规定时必须优先调用。",

            "parameters": {

                "type": "object",

                "properties": {

                    "question": {

                        "type": "string",

                        "description":
                            "需要查询企业知识库的问题。"

                    }

                },

                "required": [
                    "question"
                ]

            }
        }
    },


    # ==================================================
    # Travel Expense Calculator
    # ==================================================

    {
        "type": "function",

        "function": {

            "name":
                "calculate_travel_expense",

            "description":
                "计算企业差旅费用。"
                "适用于住宿费、伙食补助、"
                "市内交通补助等费用。",

            "parameters": {

                "type": "object",

                "properties": {

                    "expense_type": {

                        "type": "string",

                        "description":
                            "费用类型，例如：住宿、伙食、"
                            "市内交通"

                    },

                    "quantity": {

                        "type": "number",

                        "description":
                            "费用数量，例如住宿晚数、"
                            "伙食天数"

                    },

                    "unit_price": {

                        "type": "number",

                        "description":
                            "费用单价，例如420或120"

                    }

                },

                "required": [
                    "expense_type",
                    "quantity",
                    "unit_price"
                ]

            }
        }
    }

]


# ==================================================
# 7. Agent Step 名称
# ==================================================

STEP_LABELS = {

    "agent_planning":
        "正在分析需求...",

    "knowledge_search":
        "正在查询企业差旅制度...",

    "calculator":
        "正在计算费用...",

    "calculate_travel_expense":
        "正在计算差旅费用...",

    "final_answer":
        "正在生成最终回答..."

}


# ==================================================
# 8. Agent 主函数
# ==================================================

def run_agent(user_input):

    """
    执行一次完整的企业差旅 Agent。

    返回：

        answer
        steps
        sources
        total_duration_ms
    """

    total_start_time = time.perf_counter()


    # ==================================================
    # 消息历史
    # ==================================================

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "user",
            "content": user_input
        }

    ]


    # ==================================================
    # Agent 执行轨迹
    # ==================================================

    steps = [

        {
            "tool":
                "agent_planning",

            "label":
                STEP_LABELS[
                    "agent_planning"
                ],

            "status":
                "success",

            "duration_ms":
                0

        }

    ]


    # ==================================================
    # 来源
    # ==================================================

    sources = []


    # ==================================================
    # 最大 Agent Loop
    # ==================================================

    MAX_STEPS = 10

    step = 0


    # ==================================================
    # Agent Loop
    # ==================================================

    while step < MAX_STEPS:

        step += 1

        print(
            f"\n========== Agent 第 {step} 轮 =========="
        )


        # ==================================================
        # LLM 调用
        # ==================================================

        llm_start_time = time.perf_counter()

        try:

            response = client.chat.completions.create(

                model="qwen-plus",

                messages=messages,

                tools=tools,

                tool_choice="auto"

            )

        except Exception as e:

            total_duration_ms = round(

                (
                    time.perf_counter()
                    -
                    total_start_time
                )
                * 1000

            )

            steps.append({

                "tool":
                    "final_answer",

                "label":
                    "Agent 执行失败",

                "status":
                    "error",

                "duration_ms":
                    0

            })

            return {

                "answer":
                    f"Agent 调用失败：{str(e)}",

                "steps":
                    steps,

                "sources":
                    sources,

                "total_duration_ms":
                    total_duration_ms

            }


        llm_duration_ms = round(

            (
                time.perf_counter()
                -
                llm_start_time
            )
            * 1000

        )


        # ==================================================
        # 获取 Assistant Message
        # ==================================================

        message = response.choices[0].message


        # ==================================================
        # 没有 Tool Call
        # ==================================================

        if not message.tool_calls:

            print(
                "\n最终AI回答："
            )

            print(
                message.content
            )


            steps.append({

                "tool":
                    "final_answer",

                "label":
                    STEP_LABELS[
                        "final_answer"
                    ],

                "status":
                    "success",

                "duration_ms":
                    llm_duration_ms

            })


            total_duration_ms = round(

                (
                    time.perf_counter()
                    -
                    total_start_time
                )
                * 1000

            )


            # ==================================================
            # 来源去重
            # ==================================================

            unique_sources = []

            seen_sources = set()

            for source in sources:

                source_key = json.dumps(
                    source,
                    ensure_ascii=False,
                    sort_keys=True
                )

                if source_key not in seen_sources:

                    seen_sources.add(
                        source_key
                    )

                    unique_sources.append(
                        source
                    )


            return {

                "answer":
                    message.content,

                "steps":
                    steps,

                "sources":
                    unique_sources,

                "total_duration_ms":
                    total_duration_ms

            }


        # ==================================================
        # 保存 Assistant Tool Call
        # ==================================================

        messages.append(message)


        # ==================================================
        # 处理 Tool Calls
        # ==================================================

        for tool_call in message.tool_calls:

            tool_name = (
                tool_call.function.name
            )


            try:

                arguments = json.loads(

                    tool_call.function.arguments

                )

            except json.JSONDecodeError:

                arguments = {}


            print(
                "\nAI决定调用工具：",
                tool_name
            )

            print(
                "工具参数：",
                arguments
            )


            # ==================================================
            # Tool 开始
            # ==================================================

            tool_start_time = (
                time.perf_counter()
            )


            tool_status = "success"


            # ==================================================
            # Calculator
            # ==================================================

            if tool_name == "calculator":

                result = calculator(

                    arguments.get(
                        "expression",
                        ""
                    )

                )


            # ==================================================
            # Knowledge Search
            # ==================================================

            elif tool_name == "knowledge_search":

                question = arguments.get(
                    "question",
                    user_input
                )

                result = knowledge_search(
                    question
                )


                print(
                    "\nKnowledge Search Tool 返回结果："
                )

                print(
                    result
                )


                # ==================================================
                # 提取来源
                # ==================================================

                try:

                    knowledge_result = json.loads(
                        result
                    )


                    result_sources = (
                        knowledge_result.get(
                            "sources",
                            []
                        )
                    )


                    if result_sources:

                        sources.extend(
                            result_sources
                        )

                except Exception:

                    pass


            # ==================================================
            # Travel Expense Calculator
            # ==================================================

            elif (
                tool_name ==
                "calculate_travel_expense"
            ):

                result = calculate_travel_expense(

                    expense_type=
                        arguments.get(
                            "expense_type",
                            ""
                        ),

                    quantity=
                        arguments.get(
                            "quantity",
                            0
                        ),

                    unit_price=
                        arguments.get(
                            "unit_price",
                            0
                        )

                )


            # ==================================================
            # Unknown Tool
            # ==================================================

            else:

                result = json.dumps({

                    "error":
                        f"未知的工具：{tool_name}"

                }, ensure_ascii=False)

                tool_status = "error"


            # ==================================================
            # Tool 执行时间
            # ==================================================

            duration_ms = round(

                (
                    time.perf_counter()
                    -
                    tool_start_time
                )
                * 1000

            )


            # ==================================================
            # Agent Step
            # ==================================================

            steps.append({

                "tool":
                    tool_name,

                "label":
                    STEP_LABELS.get(

                        tool_name,

                        f"正在执行：{tool_name}"

                    ),

                "arguments":
                    arguments,

                "status":
                    tool_status,

                "duration_ms":
                    duration_ms

            })


            print(

                f"Tool 执行完成："
                f"{tool_name} · "
                f"{duration_ms}ms"

            )


            # ==================================================
            # Tool Result
            # ==================================================

            messages.append({

                "role":
                    "tool",

                "tool_call_id":
                    tool_call.id,

                "content":
                    result

            })


    # ==================================================
    # 超过最大轮数
    # ==================================================

    total_duration_ms = round(

        (
            time.perf_counter()
            -
            total_start_time
        )
        * 1000

    )


    steps.append({

        "tool":
            "final_answer",

        "label":
            "Agent 执行超过最大轮数",

        "status":
            "error",

        "duration_ms":
            0

    })


    return {

        "answer":
            "Agent 执行超过最大轮数，请稍后重试。",

        "steps":
            steps,

        "sources":
            sources,

        "total_duration_ms":
            total_duration_ms

    }


# ==================================================
# 9. 命令行测试
# ==================================================

if __name__ == "__main__":

    user_input = input(
        "\n请输入你的问题："
    )


    result = run_agent(
        user_input
    )


    print(
        "\n========== 最终结果 =========="
    )

    print(
        result["answer"]
    )


    print(
        "\n========== Agent Steps =========="
    )

    for step in result["steps"]:

        print(
            step
        )


    print(
        "\n========== Sources =========="
    )

    for source in result["sources"]:

        print(
            source
        )


    print(
        "\n========== 总耗时 =========="
    )

    print(
        result["total_duration_ms"],
        "ms"
    )