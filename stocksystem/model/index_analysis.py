from sqlalchemy import Column, Integer, Date, JSON, TIMESTAMP
from model.__init__ import db

class IndexAnalysis(db.Model):
    __tablename__ = 'index_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(Date, nullable=False)
    sh_index = Column(JSON)
    sz_index = Column(JSON)
    cyb_index = Column(JSON)
    kc50_index = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())