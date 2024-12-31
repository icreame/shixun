from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class News(db.Model):
    __tablename__ = 'news'

    # 数据库字段定义
    newsid = db.Column(db.Integer, primary_key=True, autoincrement=True)    # 新闻唯一标识
    title = db.Column(db.String(200), nullable=False)                        # 新闻标题
    publishdate = db.Column(db.Date, nullable=False)                         # 新闻发布时间
    content = db.Column(db.Text, nullable=False)                             # 新闻内容
    sourceid = db.Column(db.Integer, db.ForeignKey('source.sourceid'), nullable=False)  # 外键，关联数据来源
    industryid = db.Column(db.Integer, db.ForeignKey('industry.industryid'), nullable=False)  # 外键，关联行业
    sentimentid = db.Column(db.Integer, db.ForeignKey('sentiment.sentimentid'), nullable=False)  # 外键，关联情感
    stockid = db.Column(db.Integer, db.ForeignKey('stock.stockid'), nullable=False)  # 外键，关联股票表

    # 外键关系
    source = db.relationship('Source', backref='news', lazy=True)
    industry = db.relationship('Industry', backref='news', lazy=True)
    sentiment = db.relationship('Sentiment', backref='news', lazy=True)
    stock = db.relationship('Stock', backref='news', lazy=True)

    def __repr__(self,newsid, title, publishdate, content, sourceid, industryid, sentimentid, stockid):
        self.newsid = newsid
        self.title=title
        self.stockid=stockid
        self.publishdate = publishdate
        self.sourceid = sourceid
        self.sentimentid = sentimentid
        self.industryid=industryid
        self.content=content
