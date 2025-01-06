from model.__init__ import db

class SelfSelect(db.Model):
    __tablename__ = 'selfselect'
    __table_args__ = {'extend_existing': True}
    # 组合主键，确保每个用户只能选择每只股票一次
    stockid = db.Column(db.Integer, db.ForeignKey('stock.stockid'), primary_key=True)  # 外键，关联股票表
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), primary_key=True)    # 外键，关联用户表

    # user = db.relationship('User', backref=db.backref('selfselects_user', lazy=True))  # 自选股与用户的关系
    # # 关联字段
    # stock = db.relationship('Stock', backref=db.backref('selfselects_ref', lazy=True))  # 自选股与股票的关系
    # user = db.relationship('User', backref=db.backref('selfselects', lazy=True))  # 自选股与用户的关系

    def __repr__(self):
        return f"<SelfSelect(stockid={self.stockid}, userid={self.userid})>"
