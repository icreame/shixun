from model.__init__ import db

class Source(db.Model):
    __tablename__ = 'source'

    # 数据库字段定义
    sourceid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 数据来源唯一标识
    sourcename = db.Column(db.String(50), nullable=False)                   # 数据来源名称
    description = db.Column(db.Text)                                        # 描述

    def __repr__(self,sourceid,sourcename,description=None):
        self.sourceid=sourceid
        self.sourcename=sourcename
        self.description=description
