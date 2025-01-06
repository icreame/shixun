from model.news import News,db
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
            content=content,
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
                "content": news.content,
                "publishdate": news.publishdate if news.publishdate else "未知",
                "source": news.source.sourcename if news.source else "未知",
                "industry": news.industry.industryname if news.industry else "未知",
                "sentiment": news.sentiment.sentimenttype if news.sentiment else "未知",
                "stock": news.stock.stockname if news.stock and news.stock else "未知"
            }]
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
