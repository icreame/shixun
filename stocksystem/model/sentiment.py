from model.__init__ import db


class Sentiment(db.Model):
    __tablename__ = 'sentiment'

    # 数据库字段定义
    sentimentid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 情感唯一标识
    sentiment =db.Column(db.String(200))
    score = db.Column(db.Double)

    def __repr__(self, sentimentid, sentiment, score):
        self.sentimentid = sentimentid
        self.sentiment = sentiment
        self.score = score

