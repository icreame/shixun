import httpx
import mysql.connector
import pandas as pd
from gdeltdoc import GdeltDoc, Filters
import urllib.parse
import time
import json
from openai import OpenAI
import asyncio
from gdeltdoc import GdeltDoc

from model.news import News,db
from model.sentiment import Sentiment
from model.stock import Stock
from model.industry import Industry
from model.source import  Source
from flask_sqlalchemy import SQLAlchemy


class NewsService:

    @staticmethod
    def add_news(title, url, content, publishdate, sourceid, industryid, sentimentid, stockid):
        """
        添加新闻
        """
        new_news = News(
            title=title,
            url=url,
            content=content or None,
            publishdate=publishdate or None,
            sourceid=sourceid or None,
            industryid=industryid or None,
            sentimentid=sentimentid or None,
            stockid=stockid or None
        )
        try:
            db.session.add(new_news)
            db.session.commit()
            return new_news  # 返回新闻对象
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_news_by_id(newsid):
        """
        根据新闻ID获取新闻
        """
        try:
            news = News.query.get(newsid)
            news_list = [{
                "newsid": news.newsid,
                "title": news.title,
                "url": news.url,

                "content": news.content if news.content else None,
                "publishdate": news.publishdate if news.publishdate else None,

            }]
            if news.sourceid:
                source=Source.query.get(news.sourceid)
                news_list.append(source.sourcename)
            if news.industryid:
                industry=Industry.query.get(news.industryid)
                news_list.append(industry.industryname)
            if news.sentimentid:
                sentiment=Sentiment.query.get(news.sentimentid)
                news_list.append(sentiment.sentimenttype)
            if news.stockid:
                stock=Stock.query.get(news.stockid)
                news_list.append(stock.stockname)
            return {"success": True, "data": news_list}
        except Exception as e:
            return {"success": False, "message": f"获取新闻信息失败: {str(e)}"}

    @staticmethod
    def get_all_news(page, per_page):
        """
        获取所有新闻
        """
        try:
            new_news = News.query.paginate(page=page, per_page=per_page, error_out=False).items
            total_news = News.query.count()
            news_list = [{
                "newsid": news.newsid,
                "title": news.title,
                "url": news.url,
                "content": news.content,
                "publishdate": news.publishdate if news.publishdate else "未知",
                "source": news.source.sourcename if news.source else "未知",
                "industry": news.industry.industryname if news.industry else "未知",
                "sentiment": news.sentiment.sentiment if news.sentiment else "未知",
                "stock": news.stock.stockname if news.stock and news.stock else "未知"
            } for news in new_news]

            return {"total": total_news,"data": news_list}
        except Exception as e:
            return {"success": False, "message": f"获取新闻信息失败: {str(e)}"}

    @staticmethod
    def delete_news(newsid):
        """
        删除新闻
        """
        news = News.query.get(newsid)
        if news:
            try:
                db.session.delete(news)
                db.session.commit()
                return {"success": True, "message": "新闻已删除"}
            except Exception as e:
                db.session.rollback()
                return {"success": False, "message": str(e)}
        else:
            return {"success": False, "message": "新闻不存在"}

    @staticmethod
    def update_news(newsid, title=None, url=None, content=None, publishdate=None, sourceid=None, industryid=None,
                    sentimentid=None, stockid=None):
        """
        更新新闻信息
        """
        news = News.query.get(newsid)
        if not news:
            return {"success": False, "message": "新闻不存在"}

        try:
            if title:
                news.title = title
            if url:
                news.url = url
            if content:
                news.content = content
            if publishdate:
                news.publishdate = publishdate
            if sourceid:
                news.sourceid = sourceid
            if industryid:
                news.industryid = industryid
            if sentimentid:
                news.sentimentid = sentimentid
            if stockid:
                news.stockid = stockid

            db.session.commit()
            return {"success": True, "message": "新闻已更新"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    async def fetch_and_analyze_news(keyword):
        """
        从 API 获取新闻数据并调用大语言模型进行分析
        """
        # 初始化 GDELT
        gd = GdeltDoc()

        # 获取新闻数据
        encoded_keyword = urllib.parse.quote(keyword)
        f = Filters(
            keyword=encoded_keyword,
            start_date="2025-01-01",  # 调整为过去的时间
            end_date="2025-01-06",
            num_records=5,  # 仅获取 5 条新闻用于测试
            country="China",
            language="Chinese"
        )
        try:
            articles = gd.article_search(f)
            if not articles.empty:
                analysis_results = []
                news_data = []  # 用于存储新闻数据
                analysis_data = []  # 用于存储分析结果

                for article in articles.to_dict("records"):
                    # 调用大语言模型分析新闻
                    analysis_result = await NewsService.analyze_news_with_llm(article.get("title"))
                    analysis_results.append(analysis_result)

                    # 将新闻数据存储到列表中
                    news_data.append({
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "content": None,            # 【0106 暂时需要content为空】
                        "publishdate": article.get("publish_date"),
                        "sourceid": None,  # 根据实际情况填写
                        "industryid": None,  # 根据实际情况填写
                        "sentimentid": None,  # 根据实际情况填写
                        "stockid": None  # 根据实际情况填写
                    })

                    # 将分析结果存储到列表中
                    analysis_data.append({
                        "title": article.get("title"),
                        "analysis_result": analysis_result
                    })

                # # 异步将数据存储到数据库
                # asyncio.create_task(NewsService.save_data_to_db(news_data, analysis_data))

                # 异步将数据存储到数据库[用于测试为什么数据库没写入]
                await NewsService.save_data_to_db(news_data, analysis_data)  # 使用 await 确保任务完成

                return {"success": True, "data": analysis_results}
            else:
                return {"success": False, "message": f"关键字 '{keyword}' 未能获取任何数据。"}
        except Exception as e:
            return {"success": False, "message": f"关键字 '{keyword}' 查询失败，错误信息: {e}"}

    @staticmethod
    async def save_data_to_db(news_data, analysis_data):
        """
        异步将新闻数据和分析结果存储到数据库
        """
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="shixun",
                password="123456",
                database="stocksystem"
            )
            cursor = conn.cursor()

            # 存储新闻数据到 news 表
            for news in news_data:
                # 如果 content 为空，设置默认值
                content = news["content"] if news["content"] else "无内容"

                cursor.execute("""
                    INSERT INTO news (title, url, content, publishdate, sourceid, industryid, sentimentid, stockid)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    news["title"],
                    news["url"],
                    content,  # 使用处理后的 content
                    news["publishdate"],
                    news["sourceid"],
                    news["industryid"],
                    news["sentimentid"],
                    news["stockid"]
                ))

                # 获取刚插入的新闻的 ID
                news_id = cursor.lastrowid
                print(f"插入新闻数据成功，news_id: {news_id}")  # 打印日志

                # 存储分析结果到 news_analysis 表
                for analysis in analysis_data:
                    if analysis["title"] == news["title"]:
                        cursor.execute("""
                            INSERT INTO news_analysis (news_id, sector, trend, reason, sentiment)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            news_id,
                            analysis["analysis_result"].get("板块"),
                            analysis["analysis_result"].get("走势"),
                            analysis["analysis_result"].get("理由"),
                            analysis["analysis_result"].get("情感标签")
                        ))
                        print(f"插入分析结果成功，news_id: {news_id}")  # 打印日志

            conn.commit()  # 提交事务
            print("数据存储成功")  # 打印日志
        except Exception as e:
            conn.rollback()  # 回滚事务
            print(f"数据库存储失败: {e}")  # 打印日志
        finally:
            if conn.is_connected():  # 检查连接是否仍然打开
                cursor.close()
                conn.close()
                print("数据库连接已关闭")  # 打印日志

    @staticmethod
    async def analyze_news_with_llm(news_title):      # 尝试删除content字段
        """
        调用大语言模型分析新闻
        """
        api_key = "sk-10465596f9e847e389a5e22f10c8e58d"
        base_url = "https://api.deepseek.com/v1/chat/completions"  # 替换为实际的 API 地址

        system_prompt = """
            用户将提供批量的新闻的内容，请分析每一条新闻，分析新闻对应的板块和走势，请以json格式输出板块名字，看涨还是看跌，分析的理由，该条新闻的情感标签（正面，负面，中性）
            """

        user_prompt = f"请分析我给你的新闻，用json格式给出输出，新闻如下：{news_title}\n"

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
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            return json.loads(content)
