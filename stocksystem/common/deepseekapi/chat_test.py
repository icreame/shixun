# Please install OpenAI SDK first: `pip3 install openai`
import json
from openai import OpenAI

# 使用json格式对文本进行分析

client = OpenAI(
    api_key="sk-10465596f9e847e389a5e22f10c8e58d",
    base_url="https://api.deepseek.com",
)

system_prompt = """
用户将提供批量的新闻的内容，请分析每一条新闻，分析新闻对应的板块和走势，请以json格式输出板块名字，看涨还是看跌，分析的理由，该条新闻的情感标签（正面，负面，中性）
输入示例：
新闻内容：油气开采服务板块开盘拉升，首华燃气涨超6%,每经AI快讯，油气开采服务板块开盘拉升，首华燃气涨超6%，科力股份、仁智股份、潜能恒信、贝肯能源等均涨超2%。
输出示例：
{
    "板块": "燃气",
    "走势": "看涨",
    "理由": "油气开采服务板块开盘拉升，首华燃气涨超6%，科力股份、仁智股份、潜能恒信、贝肯能源等均涨超2%。板块整体表现强劲，市场情绪积极。",
    "情感标签": "正向"
}
"""

user_prompt = "请分析我给你的新闻，用json格式给出输出，新闻如下：中信证券：春节前情绪逐渐降温 春节后布局春季攻势"

messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    response_format={
        'type': 'json_object'
    }
)

print(json.loads(response.choices[0].message.content))