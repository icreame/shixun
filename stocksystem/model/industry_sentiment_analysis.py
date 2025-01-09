from sqlalchemy import Column, Integer, Date, JSON, TIMESTAMP
import datetime
from model.__init__ import db       # 需要继承这个base类才行


class IndustrySentimentAnalysis(db.Model):
    __tablename__ = 'industry_sentiment_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(Date, nullable=False)
    whole_analysis = Column(JSON)
    recommend_sector = Column(JSON)
    reason = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)