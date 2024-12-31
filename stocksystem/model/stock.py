from model.__init__ import db

class Stock(db.Model):
    __tablename__ = 'stock'

    # 数据库字段定义
    stockid = db.Column(db.Integer, primary_key=True, autoincrement=True)                      # 股票唯一标识符
    stockname = db.Column(db.String(100), nullable=False)                   # 股票名称
    stockprice = db.Column(db.Float, nullable=False)                        # 股票价格
    industryid = db.Column(db.Integer, db.ForeignKey('industry.industryid'), nullable=False)  # 外键，关联行业表

    industry = db.relationship("Industry", backref=db.backref("stocks", lazy=True))

    def __repr__(self,stockname, stockprice, industryid):
        self.stockname = stockname
        self.stockprice = stockprice
        self.industryid = industryid
