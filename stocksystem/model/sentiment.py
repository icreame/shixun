from model.__init__ import db

class Sentiment(db.Model):
    __tablename__ = 'sentiment'

    # 数据库字段定义
    sentimentid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 情感唯一标识
    sentimenttype = db.Column(db.String(20), nullable=False)                   # 情感类别
    description = db.Column(db.Text)                                           # 描述

    def __repr__(self,sentimentid,sentimenttype, description=None):
        self.sentimentid = sentimentid
        self.description= description
        self.sentimenttype = sentimenttype
