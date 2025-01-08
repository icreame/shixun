from sqlalchemy import Column, Integer, Date, JSON, TIMESTAMP
from model.__init__ import db

# 对大盘指数分析的结果，数据库
class IndexAnalysisResult(db.Model):
    __tablename__ = 'index_analysis_result'

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(Date, nullable=False)
    sh_index_analysis = Column(JSON)
    sz_index_analysis = Column(JSON)
    cyb_index_analysis = Column(JSON)
    kc50_index_analysis = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

