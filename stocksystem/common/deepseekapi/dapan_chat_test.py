import json
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-10465596f9e847e389a5e22f10c8e58d",  # 替换为你的 API Key
    base_url="https://api.deepseek.com",
)

# 定义系统提示词
system_prompt = """
用户将提供每日的大盘数据，请分析大盘的走势，并给出预测、理由以及情感标签（正面，负面，中性）。请以json格式输出预测结果。
输入示例：
大盘数据：上证指数今日收盘上涨1.5%，成交量较昨日增加10%，市场情绪积极。
输出示例：
{
    "预测": "看涨",
    "理由": "上证指数今日收盘上涨1.5%，成交量较昨日增加10%，市场情绪积极，预计短期内市场将继续上涨。",
    "情感标签": "正向"
}
"""


def analyze_market_data(market_data):
    """
    通过传入的大盘数据调用大模型进行分析，并返回 JSON 格式的结果。

    :param market_data: 字符串，包含大盘数据信息
    :return: JSON 对象，包含预测、理由和情感标签
    """
    # 用户提示词，传入大盘数据
    user_prompt = f"请分析我给你的大盘数据，用json格式给出输出，大盘数据如下：{market_data}"

    # 构建消息列表
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # 调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={'type': 'json_object'}  # 指定返回 JSON 格式
    )

    # 解析并返回结果
    return json.loads(response.choices[0].message.content)


# 示例调用
if __name__ == "__main__":
    # 示例大盘数据
    market_data = "上证指数今日收盘下跌0.8%，成交量较昨日减少5%，市场情绪较为谨慎。"

    # 调用函数进行分析
    result = analyze_market_data(market_data)

    # 打印结果
    print(json.dumps(result, indent=4, ensure_ascii=False))