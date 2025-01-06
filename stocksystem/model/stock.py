from model.__init__ import db

from stocksystem.model.selfselect import SelfSelect


class Stock(db.Model):
    __tablename__ = 'stock'
    __table_args__ = {'extend_existing': True}

    # 数据库字段定义
    stockid = db.Column(db.Integer, primary_key=True, autoincrement=True)                      # 股票唯一标识符
    stockcode = db.Column(db.Integer, nullable=False)                       # 股票代码
    stockname = db.Column(db.String(100), nullable=False)                   # 股票名称
    stockprice = db.Column(db.Float)                        # 股票价格
    industryid = db.Column(db.Integer)  # 外键，关联行业表


    def __repr__(self,stockname, stockcode,stockprice, industryid):
        self.stockcode = stockcode
        self.stockname = stockname
        self.stockprice = stockprice
        self.industryid = industryid
