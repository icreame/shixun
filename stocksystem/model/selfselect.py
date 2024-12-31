from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class SelfSelect(db.Model):
    __tablename__ = 'selfselect'

    # 组合主键，确保每个用户只能选择每只股票一次
    stockid = db.Column(db.Integer, db.ForeignKey('stock.stockid'), primary_key=True)  # 外键，关联股票表
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), primary_key=True)    # 外键，关联用户表

    # 外键关系
    stock = db.relationship('Stock', backref='selfselects', lazy=True)  # 股票与自选股的关系
    user = db.relationship('User', backref='selfselects', lazy=True)    # 用户与自选股的关系

    def __repr__(self,userid, stockid):
        self.userid = userid
        self.stockid = stockid
