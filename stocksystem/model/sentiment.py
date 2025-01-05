from model.__init__ import db

class Sentiment(db.Model):
    __tablename__ = 'sentiment'

    # 数据库字段定义
    sentimentid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 情感唯一标识
    positive = db.Column(db.Double, nullable=False)
    negative = db.Column(db.Double, nullable=False)
    sentiment =db.Column(db.String(200))

    def __repr__(self,sentimentid,positive, negative,sentiment):
        self.sentimentid = sentimentid
        self.positive = positive
        self.negative = negative
        self.sentiment = sentiment
