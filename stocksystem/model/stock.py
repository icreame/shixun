from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Stock(db.Model):
    __tablename__ = 'stock'

    # 数据库字段定义
    stockid = db.Column(db.Integer, primary_key=True, autoincrement=True)                      # 股票唯一标识符
    stockname = db.Column(db.String(100), nullable=False)                   # 股票名称
    stockprice = db.Column(db.Float, nullable=False)                        # 股票价格
    industryid = db.Column(db.Integer, db.ForeignKey('industry.industryid'), nullable=False)  # 外键，关联行业表

    # 外键关系
    industry = db.relationship('Industry', backref='stocks', lazy=True)    # 行业与股票的关系

    def __repr__(self,stockid, stockname, stockprice, industryid):
        self.stockid = stockid
        self.stockname = stockname
        self.stockprice = stockprice
        self.industryid = industryid
