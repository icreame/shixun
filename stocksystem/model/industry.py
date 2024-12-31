from model.__init__ import db

class Industry(db.Model):
    __tablename__ = 'industry'

    # 数据库字段定义
    industryid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 行业唯一标识
    industryname = db.Column(db.String(50), nullable=False)                   # 行业名称
    description = db.Column(db.Text)                                          # 描述

    def __repr__(self,industryid, industryname,description=None):
        self.industryid = industryid
        self.industryname=industryname
        self.description= description
