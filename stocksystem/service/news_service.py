import httpx
import mysql.connector
from google.cloud import bigquery
import json
from openai import OpenAI
import asyncio
import requests
from sqlalchemy.orm import joinedload
from sqlalchemy import func,or_
from model.analysis_result import AnalysisResult
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
        获取所有新闻及其分析结果
        :param page: 当前页码
        :param per_page: 每页显示的记录数
        :return: 包含新闻及其分析结果的 JSON 数据
        """
        try:
            # 分页查询新闻及其关联的新闻分析结果
            paginated_news = (
                News.query
                .options(joinedload(News.analysis_results))  # 使用 joinedload 预加载分析结果
                .paginate(page=page, per_page=per_page, error_out=False)
            )
            total_news = News.query.count()

            news_list = []
            for news in paginated_news.items:
                news_item = {
                    "newsid": news.newsid,
                    "title": news.title,
                    "url": news.url,
                    "content": news.content,
                    "publishdate": news.publishdate.isoformat() if news.publishdate else None,
                }

                # 添加新闻分析结果
                if news.analysis_results:
                    for analysis in news.analysis_results:
                        news_item.update({
                            "sector": analysis.sector,
                            "trend": analysis.trend,
                            "reason": analysis.reason,
                            "sentiment": analysis.sentiment,
                        })

                news_list.append(news_item)

            return {
                "total": total_news,
                "page": page,
                "per_page": per_page,
                "data": news_list,
            }
        except Exception as e:
            return {"success": False, "message": f"获取新闻及其分析结果失败: {str(e)}"}

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
    def get_sentiment_by_industry():
        """
        获取每个行业的正面和负面新闻数量
        """
        try:
            # 查询每个行业的正面和负面新闻数量
            result = (
                db.session.query(
                    Industry.industryname,
                    func.sum(func.if_(AnalysisResult.sentiment == '正面', 1, 0)).label('positive_count'),
                    func.sum(
                        func.if_(or_(
                            AnalysisResult.sentiment == '负面',
                            AnalysisResult.sentiment == '中性'
                        ), 1, 0)
                    ).label('negative_count')
                )
                .join(News, News.industryid == Industry.industryid)
                .join(AnalysisResult, AnalysisResult.news_id == News.newsid)
                .group_by(Industry.industryname)
                .all()
            )

            # 将结果转换为字典格式
            sentiment_data = [
                {
                    "industry": row.industryname,
                    "positive": row.positive_count,
                    "negative": row.negative_count
                }
                for row in result
            ]

            return {"success": True, "data": sentiment_data}
        except Exception as e:
            return {"success": False, "message": f"获取情感分析数据失败: {str(e)}"}


    @staticmethod
    def search_news_by_industry_and_sentiment(industryid=None, sentiment=None, page=1, per_page=10,
                                              sort_by="publishdate", order="desc"):
        """
        根据行业和情感标签搜索新闻，支持分页和排序
        :param industryid: 行业ID
        :param sentiment: 情感标签（如 "正面", "负面", "中性"）
        :param page: 当前页码
        :param per_page: 每页显示的新闻数量
        :param sort_by: 排序字段（如 "publishdate"）
        :param order: 排序顺序（"asc" 或 "desc"）
        :return: 分页后的新闻列表
        """
        try:
            # 构建基础查询
            query = News.query.join(AnalysisResult, News.newsid == AnalysisResult.news_id)

            # 根据行业筛选
            if industryid:
                query = query.filter(News.industryid == industryid)

            # 根据情感标签筛选
            if sentiment:
                query = query.filter(AnalysisResult.sentiment == sentiment)

            # 排序
            if sort_by == "publishdate":
                if order == "desc":
                    query = query.order_by(News.publishdate.desc())
                else:
                    query = query.order_by(News.publishdate.asc())

            # 分页查询
            news_list = query.paginate(page=page, per_page=per_page, error_out=False)

            # 构建返回结果
            result = []
            for news in news_list.items:
                # 获取新闻的情感标签（假设每条新闻只有一条分析结果）
                sentiment_tag = None
                if news.analysis_results:  # 检查是否有分析结果
                    sentiment_tag = news.analysis_results[0].sentiment
                    reason = news.analysis_results[0].reason
                    trend = news.analysis_results[0].trend
                    sector = news.analysis_results[0].sector

                result.append({         # 【0108】新增reason删除content
                    "newsid": news.newsid,
                    "title": news.title,
                    "url": news.url,
                    "publishdate": news.publishdate.strftime("%Y-%m-%d") if news.publishdate else None,
                    "sourceid": news.sourceid if news.sourceid else None,
                    "industryid": news.industryid if news.industryid else None,
                    "sentimentid": news.sentimentid if news.sentimentid else None,
                    "stockid": news.stockid if news.stockid else None,
                    "sentiment": sentiment_tag,  # 添加情感标签
                    "reason": reason,
                    "trend": trend,
                    "industryname": sector
                })

            return {
                "success": True,
                "data": result,
                "total": news_list.total,
                "page": news_list.page,
                "per_page": news_list.per_page
            }
        except Exception as e:
            return {"success": False, "message": f"搜索新闻失败: {str(e)}"}

    # TODO：本地跑的，所以注释掉了，应该没有影响
    # @staticmethod
    # def fetch_and_analyze_news(keyword, start_date="2025-01-01", end_date="2025-01-06", num_records=20):
    #     """
    #     从 API 获取新闻数据并调用大语言模型进行分析
    #     """
    #
    #     # TODO
    #     client = bigquery.Client()
    #     # 根据股票名称构建查询
    #     query = f"""
    #             SELECT FORMAT_TIMESTAMP('%Y-%m-%d', date) AS date, url, title
    #             FROM `gdelt-bq.gdeltv2.gqg`
    #             WHERE date BETWEEN TIMESTAMP('{start_date}') AND TIMESTAMP('{end_date}')
    #                   AND lang = 'Chinese'
    #                   AND title LIKE '%{keyword}%';
    #         """
    #
    #     try:
    #         # 执行查询并获取数据
    #         articles = client.query(query).result()
    #         if articles.total_rows > 0:
    #             # 同步调用大语言模型分析新闻
    #             paired_data = []
    #             for article in articles:
    #                 analysis_result = NewsService.analyze_news_with_llm(article.title)
    #
    #                 paired_data.append({
    #                     "news": {
    #                         "title": article.title,
    #                         "url": article.url,
    #                         "content": None,  # 【0106 暂时需要content为空】
    #                         "publishdate": article.date,
    #                         "sourceid": None,  # 根据实际情况填写
    #                         "industryid": None,  # 根据实际情况填写
    #                         "sentimentid": None,  # 根据实际情况填写
    #                         "stockid": None,  # 根据实际情况填写
    #                     },
    #                     "analysis": {
    #                         "title": article.title,
    #                         "analysis_result": analysis_result
    #                     }
    #                 })
    #
    #             # TODO
    #             # 存储数据到数据库
    #             NewsService.save_data_to_db(paired_data, keyword)
    #
    #             return {"success": True, "data": [item["analysis"]["analysis_result"] for item in paired_data]}
    #         else:
    #             return {"success": False, "message": f"关键字 '{keyword}' 未能获取任何数据。"}
    #     except Exception as e:
    #         return {"success": False, "message": f"关键字 '{keyword}' 查询失败，错误信息: {e}"}
    #
    # @staticmethod
    # def save_data_to_db(paired_data, keyword):
    #     """
    #     同步将新闻数据和分析结果存储到数据库
    #     """
    #     try:
    #         conn = mysql.connector.connect(
    #             host="localhost",
    #             user="shixun",
    #             password="123456",
    #             database="stocksystem"
    #         )
    #         cursor = conn.cursor()
    #
    #         # 存储新闻数据到 news 表
    #         for pair in paired_data:
    #             news = pair["news"]
    #             analysis = pair["analysis"]
    #
    #             # 如果 content 为空，设置默认值
    #             content = news["content"] if news["content"] else "无内容"
    #
    #             # 插入新闻数据
    #             cursor.execute("""
    #                     INSERT INTO news (title, url, content, publishdate, sourceid, industryid, sentimentid, stockid)
    #                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    #                 """, (
    #                 news["title"],
    #                 news["url"],
    #                 content,  # 使用处理后的 content
    #                 news["publishdate"],
    #                 news["sourceid"],
    #                 news["industryid"],
    #                 news["sentimentid"],
    #                 news["stockid"]
    #             ))
    #
    #             # 获取刚插入的新闻的 ID
    #             news_id = cursor.lastrowid
    #             print(f"插入新闻数据成功，news_id: {news_id}")  # 打印日志
    #
    #             # 插入分析结果
    #             cursor.execute("""
    #                     INSERT INTO news_analysis (news_id, sector, trend, reason, sentiment)
    #                     VALUES (%s, %s, %s, %s, %s)
    #                 """, (
    #                 news_id,
    #                 keyword,  # 将 keyword 插入到 sector 字段
    #                 analysis["analysis_result"].get("走势"),
    #                 analysis["analysis_result"].get("分析的理由"),      # 【0107】这里标签的名字出错了，所以之前的理由无法存入数据库
    #                 analysis["analysis_result"].get("情感标签")
    #             ))
    #             print(f"插入分析结果成功，news_id: {news_id}")  # 打印日志
    #
    #         conn.commit()  # 提交事务
    #         print("数据存储成功")  # 打印日志
    #     except Exception as e:
    #         conn.rollback()  # 回滚事务
    #         print(f"数据库存储失败: {e}")  # 打印日志
    #     finally:
    #         if conn.is_connected():  # 检查连接是否仍然打开
    #             cursor.close()
    #             conn.close()
    #             print("数据库连接已关闭")  # 打印日志
    #
    # @staticmethod
    # def analyze_news_with_llm(news_title):
    #     """
    #     调用大语言模型分析新闻
    #     """
    #     api_key = "sk-10465596f9e847e389a5e22f10c8e58d"
    #     base_url = "https://api.deepseek.com/v1/chat/completions"  # 替换为实际的 API 地址
    #
    #     system_prompt = """
    #                 用户将提供批量的新闻的内容，请分析每一条新闻，分析新闻对应的板块和走势，请以json格式输出板块名字，看涨还是看跌，分析的理由，该条新闻的情感标签（正面，负面，中性）
    #                 """
    #
    #     user_prompt = f"请分析我给你的新闻，用json格式给出输出，新闻如下：{news_title}\n"
    #
    #     payload = {
    #         "model": "deepseek-chat",
    #         "messages": [
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_prompt}
    #         ],
    #         "response_format": {"type": "json_object"}
    #     }
    #
    #     headers = {
    #         "Authorization": f"Bearer {api_key}",
    #         "Content-Type": "application/json"
    #     }
    #
    #     # 使用同步的 requests 库发送请求
    #     response = requests.post(base_url, json=payload, headers=headers)
    #     response.raise_for_status()  # 检查请求是否成功
    #     response_data = response.json()
    #     content = response_data["choices"][0]["message"]["content"]
    #     return json.loads(content)




