import json


# ==================================================
# Travel Expense Calculator
# ==================================================

def calculate_travel_expense(
    expense_type,
    quantity,
    unit_price
):
    """
    计算差旅费用。

    参数：
        expense_type：费用类型，例如住宿、伙食、市内交通
        quantity：数量，例如住宿晚数、出差天数
        unit_price：单价，例如420元/晚、120元/天

    返回：
        JSON 格式的计算结果
    """

    try:

        total = quantity * unit_price

        result = {
            "expense_type": expense_type,
            "unit_price": unit_price,
            "quantity": quantity,
            "total": total
        }

        return json.dumps(
            result,
            ensure_ascii=False
        )

    except Exception as e:

        return json.dumps(
            {
                "error": f"计算失败：{str(e)}"
            },
            ensure_ascii=False
        )