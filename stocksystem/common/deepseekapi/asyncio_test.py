import os

import httpx
import mysql.connector
import pandas as pd
from gdeltdoc import GdeltDoc, Filters
import urllib.parse
import time
import json
from openai import OpenAI
import asyncio

# 配置
MYSQL_CONFIG = {
    "host": "localhost",  # MySQL 主机地址
    "user": "shixun",       # MySQL 用户名
    "password": "123456",  # MySQL 密码
    "database": "stocksystem"    # 数据库名称
}
KEYWORD = "Natural Gas"  # 测试关键字


# 初始化 MySQL 数据库
def init_database():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    # 创建新闻表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_internet (
            id INT AUTO_INCREMENT PRIMARY KEY,
            keyword VARCHAR(255),
            title TEXT,
            content TEXT,
            url TEXT,
            publish_date TEXT
        )
    """)
    # 创建分析结果表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            news_id INT,
            sector VARCHAR(255),
            trend VARCHAR(50),
            reason TEXT,
            sentiment VARCHAR(50),
            FOREIGN KEY (news_id) REFERENCES news_internet(id)
        )
    """)
    conn.commit()
    conn.close()


# 保存新闻到数据库
def save_news_to_db(keyword, articles):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    for article in articles:
        cursor.execute("""
            INSERT INTO news_internet (keyword, title, content, url, publish_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (keyword, article.get("title"), article.get("content"), article.get("url"), article.get("publish_date")))
    conn.commit()
    conn.close()


# 从数据库读取新闻
def get_news_from_db(keyword):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM news_internet WHERE keyword = %s", (keyword,))
    news_data = cursor.fetchall()
    conn.close()
    return news_data


# 保存分析结果到数据库
def save_analysis_to_db(news_id, analysis_result):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO news_analysis (news_id, sector, trend, reason, sentiment)
        VALUES (%s, %s, %s, %s, %s)
    """, (news_id, analysis_result.get("板块"), analysis_result.get("走势"), analysis_result.get("理由"), analysis_result.get("情感标签")))
    conn.commit()
    conn.close()


# 调用大模型分析新闻
# 调用大模型分析新闻（异步版本）
async def analyze_news_with_llm(news_title, news_content):
    api_key = "sk-10465596f9e847e389a5e22f10c8e58d"
    base_url = "https://api.deepseek.com/v1/chat/completions"  # 替换为实际的 API 地址

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

    user_prompt = f"请分析我给你的新闻，用json格式给出输出，新闻如下：{news_title}\n{news_content}"

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(base_url, json=payload, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应数据
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]  # 提取 content 字段
        return json.loads(content)  # 将 content 解析为 JSON 对象并返回


# 主函数
async def main():
    # 初始化数据库
    init_database()

    # 初始化 GDELT
    gd = GdeltDoc()

    # 获取新闻并保存到数据库
    encoded_keyword = urllib.parse.quote(KEYWORD)
    f = Filters(
        keyword=encoded_keyword,
        start_date="2023-01-01",  # 调整为过去的时间
        end_date="2023-12-31",
        num_records=5,  # 仅获取 5 条新闻用于测试
        country="China",
        language="Chinese"
    )
    try:
        articles = gd.article_search(f)
        if not articles.empty:
            save_news_to_db(KEYWORD, articles.to_dict("records"))
            print(f"关键字 '{KEYWORD}' 的新闻已保存到数据库。")
        else:
            print(f"关键字 '{KEYWORD}' 未能获取任何数据。")
    except Exception as e:
        print(f"关键字 '{KEYWORD}' 查询失败，错误信息: {e}")

    # 从数据库中读取新闻并调用大模型分析
    news_data = get_news_from_db(KEYWORD)
    tasks = []
    for news_id, title, content in news_data:
        task = asyncio.create_task(analyze_news_with_llm(title, content))
        tasks.append((news_id, task))

    for news_id, task in tasks:
        analysis_result = await task
        save_analysis_to_db(news_id, analysis_result)
        print(f"新闻ID: {news_id}")
        print(f"分析结果: {analysis_result}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
