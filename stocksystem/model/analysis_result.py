from model.__init__ import db


class AnalysisResult(db.Model):
    """
    新闻分析结果模型类，映射到 news_analysis 表
    """
    __tablename__ = 'news_analysis'  # 表名

    # 字段定义
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自增
    news_id = db.Column(db.Integer, db.ForeignKey('news.newsid'), nullable=False)  # 外键，关联 news 表的 newsid
    sector = db.Column(db.String(255))  # 板块，最大长度 255
    trend = db.Column(db.String(50))  # 走势（看涨/看跌），最大长度 50
    reason = db.Column(db.Text)  # 分析理由，文本类型
    sentiment = db.Column(db.String(50))  # 情感标签（正面/负面/中性），最大长度 50

    # 定义与 News 表的关系
    news = db.relationship('News', backref=db.backref('analysis_results', lazy=True))

    def __repr__(self):
        """
        返回对象的字符串表示
        """
        return f"<AnalysisResult id={self.id}, news_id={self.news_id}, sentiment={self.sentiment}>"
