from model.__init__ import db


class News(db.Model):
    __tablename__ = 'news'

    # 数据库字段定义
    newsid = db.Column(db.Integer, primary_key=True, autoincrement=True)    # 新闻唯一标识
    title = db.Column(db.String(200), nullable=False)                        # 新闻标题
    publishdate = db.Column(db.Date)                         # 新闻发布时间
    content = db.Column(db.Text, nullable=False)                             # 新闻内容
    url = db.Column(db.String(200), nullable=False)
    sourceid = db.Column(db.Integer, db.ForeignKey('source.sourceid'))  # 外键，关联数据来源
    industryid = db.Column(db.Integer, db.ForeignKey('industry.industryid'))  # 外键，关联行业
    sentimentid = db.Column(db.Integer, db.ForeignKey('sentiment.sentimentid'))  # 外键，关联情感
    stockid = db.Column(db.Integer, db.ForeignKey('stock.stockid'))  # 外键，关联股票表

    def __repr__(self, title, content, url):
        self.title = title
        self.content = content
        self.url = url
        # self.stockid = stockid
        # self.publishdate = publishdate
        # self.sourceid = sourceid
        # self.sentimentid = sentimentid
        # self.industryid = industryid

