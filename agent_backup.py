import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from rag import search_knowledge
from tools import calculate_travel_expense


# ==================================================
# 1. 加载 .env
# ==================================================

load_dotenv()


print(
    "API Key 是否读取成功：",
    bool(
        os.getenv("QWEN_API_KEY")
    )
)


# ==================================================
# 2. 创建千问客户端
# ==================================================

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# ==================================================
# 3. 企业差旅助手 System Prompt
# ==================================================

SYSTEM_PROMPT = """
你是一个专业的「企业差旅助手」。

你的主要任务是帮助企业员工查询差旅制度、
解释差旅政策，并根据企业制度进行差旅费用估算。

你必须严格依据企业知识库中的内容回答问题。

禁止凭常识、经验或其他企业的制度自行编造公司规定。


==================================================
一、你的主要职责
==================================================

你可以帮助用户：

1. 查询企业差旅制度
2. 查询住宿标准
3. 查询出差伙食补助
4. 查询市内交通补助
5. 查询交通费用报销规则
6. 查询报销流程
7. 根据企业制度进行差旅费用估算
8. 解释费用性质
9. 在需要计算时使用计算工具


==================================================
二、回答原则
==================================================

1. 企业制度优先

涉及以下问题时，应优先查询企业知识库：

- 差旅
- 出差
- 住宿
- 伙食补助
- 市内交通
- 交通费
- 报销
- 报销标准
- 费用标准
- 职级标准
- 出差补助
- 公司制度

不能仅凭自己的常识回答。


--------------------------------------------------

2. 不允许编造制度

如果知识库没有找到明确规定：

必须明确告诉用户：

“当前企业知识库中没有找到相关规定。”

不要自行推测。


--------------------------------------------------

3. Tool 使用原则

如果问题涉及企业制度：

必须优先使用 knowledge_search。

如果问题需要数学计算：

必须使用 calculator 或 calculate_travel_expense。

不要直接在回答中进行心算。


--------------------------------------------------

4. 多 Tool 协作

如果一个问题同时需要：

“查询制度 + 计算费用”

应该：

knowledge_search
↓
获得制度标准
↓
calculate_travel_expense
↓
计算费用
↓
汇总最终费用


--------------------------------------------------

5. 不要重复调用 Tool

如果知识库已经返回了足够的信息，
不要无意义地重复查询。


--------------------------------------------------

6. 费用性质必须说清楚

住宿标准为420元/晚，
并不代表员工一定可以获得420元。

应该表达为：

“普通员工北京住宿标准上限为420元/晚，
实际报销金额以合规票据为准，
且原则上不得超过该标准。”


--------------------------------------------------

7. 信息不足时主动询问

如果计算费用缺少关键参数：

- 出差天数
- 住宿晚数
- 员工职级
- 出发城市
- 交通方式

应先询问用户。


--------------------------------------------------

8. 非差旅问题

如果用户询问：

- 天气
- 股票
- 娱乐
- 新闻
- 个人生活
- 年假政策

不要调用差旅知识库强行回答。

应该说明：

“我是企业差旅助手，目前主要负责企业差旅制度、
费用标准和报销相关问题。”


--------------------------------------------------

9. 知识库没有答案

如果 knowledge_search 返回 found=false：

不要编造答案。

应该明确说明：

“当前企业知识库中没有找到相关规定，
因此暂时无法依据企业制度给出准确结论。”


==================================================
三、回答格式
==================================================

普通制度查询：

先给结论，
再解释制度依据，
最后给出参考来源。


费用估算：

使用清晰结构：

【费用估算】

住宿：
420元/晚 × 3晚 = 1260元

伙食：
120元/天 × 3天 = 360元

预计合计：
1620元

同时说明每项费用性质。


==================================================
四、核心身份
==================================================

你不是通用聊天机器人。

你的核心身份是：

“企业差旅助手”。

回答应该：

专业
准确
简洁
基于制度
不编造
必要时调用工具
需要计算时使用计算工具
"""


# ==================================================
# 4. Calculator Tool
# ==================================================

def calculator(expression):
    """
    执行数学计算。
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
    """

    result = search_knowledge(
        question
    )

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
                "如果需要进行数学计算，应使用此工具。",

            "parameters": {

                "type": "object",

                "properties": {

                    "expression": {

                        "type": "string",

                        "description":
                            "需要计算的数学表达式，"
                            "例如 420 * 3"

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
                "涉及企业内部规定时必须优先使用。",

            "parameters": {

                "type": "object",

                "properties": {

                    "question": {

                        "type": "string",

                        "description":
                            "需要在企业知识库中检索的问题。"

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
                "用于计算企业差旅费用。"
                "适用于住宿费、伙食补助、"
                "市内交通补助等费用计算。",

            "parameters": {

                "type": "object",

                "properties": {

                    "expense_type": {

                        "type": "string",

                        "description":
                            "费用类型，例如住宿、伙食、"
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
                            "费用单价"

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
# 7. Agent 主函数
# ==================================================

def run_agent(user_input):

    """
    执行一次完整的 Agent 对话。

    返回：

        answer
        steps
        sources
        total_duration_ms
    """

    # ==================================================
    # 总执行时间
    # ==================================================

    total_start_time = time.perf_counter()


    # ==================================================
    # 初始化消息历史
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
            "tool": "agent_planning",

            "status": "success",

            "duration_ms": 0

        }

    ]


    # ==================================================
    # 来源
    # ==================================================

    sources = []


    # ==================================================
    # Agent 最大执行轮数
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
        # 调用 LLM
        # ==================================================

        llm_start_time = time.perf_counter()


        response = client.chat.completions.create(

            model="qwen-plus",

            messages=messages,

            tools=tools

        )


        llm_duration_ms = round(

            (
                time.perf_counter()
                -
                llm_start_time
            )
            *
            1000

        )


        # ==================================================
        # 获取 LLM 消息
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


            # ==================================================
            # Final Answer
            # ==================================================

            steps.append({

                "tool": "final_answer",

                "status": "success",

                "duration_ms":
                    llm_duration_ms

            })


            # ==================================================
            # 总耗时
            # ==================================================

            total_duration_ms = round(

                (
                    time.perf_counter()
                    -
                    total_start_time
                )
                *
                1000

            )


            return {

                "answer":
                    message.content,

                "steps":
                    steps,

                "sources":
                    sources,

                "total_duration_ms":
                    total_duration_ms

            }


        # ==================================================
        # Assistant Tool Call
        # ==================================================

        messages.append(
            message
        )


        # ==================================================
        # 处理 Tool Calls
        # ==================================================

        for tool_call in message.tool_calls:

            tool_name = (
                tool_call.function.name
            )


            arguments = json.loads(

                tool_call.function.arguments

            )


            print(
                "\nAI决定调用工具：",
                tool_name
            )


            print(
                "工具参数：",
                arguments
            )


            # ==================================================
            # Tool 开始时间
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

                    arguments["expression"]

                )


            # ==================================================
            # Knowledge Search
            # ==================================================

            elif tool_name == "knowledge_search":

                result = knowledge_search(

                    arguments["question"]

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


                    if knowledge_result.get(
                        "sources"
                    ):

                        sources.extend(

                            knowledge_result[
                                "sources"
                            ]

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
                        arguments[
                            "expense_type"
                        ],

                    quantity=
                        arguments[
                            "quantity"
                        ],

                    unit_price=
                        arguments[
                            "unit_price"
                        ]

                )


            # ==================================================
            # Unknown Tool
            # ==================================================

            else:

                result = (
                    f"错误：未知的工具 {tool_name}"
                )

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
                *
                1000

            )


            # ==================================================
            # Agent Step
            # ==================================================

            steps.append({

                "tool":
                    tool_name,

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
        *
        1000

    )


    steps.append({

        "tool":
            "final_answer",

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
# 8. 命令行测试
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
        "\n========== 总耗时 =========="
    )


    print(
        result["total_duration_ms"],
        "ms"
    )