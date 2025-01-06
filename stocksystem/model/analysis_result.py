from model.__init__ import db


class AnalysisResult(db.Model):
    __tablename__ = 'news_analysis'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))  # 外键，关联新闻表
    sector = db.Column(db.String(100))  # 板块
    trend = db.Column(db.String(50))  # 走势（看涨/看跌）
    reason = db.Column(db.Text)  # 分析理由
    sentiment = db.Column(db.String(50))  # 情感标签（正面/负面/中性）

    def __repr__(self):
        return f"<AnalysisResult {self.id}>"
