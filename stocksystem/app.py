from flask import Flask, render_template, session
from controller.user_controller import user_blueprint, test_db_connection
from controller.industry_controller import industry_blueprint
from controller.news_controller import news_blueprint
from controller.selfselect_controller import selfselect_blueprint
from controller.sentiment_controller import sentiment_blueprint
from controller.source_controller import source_blueprint
from controller.stock_controller import stock_blueprint
from model.__init__ import db
from config import Config


def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    # 加载配置
    app.config.from_object(Config)

    # 初始化数据库
    db.init_app(app)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    # 注册蓝图
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(industry_blueprint, url_prefix='/industry')
    app.register_blueprint(news_blueprint, url_prefix='/news')
    app.register_blueprint(selfselect_blueprint, url_prefix='/selfselect')
    app.register_blueprint(sentiment_blueprint, url_prefix='/sentiment')
    app.register_blueprint(source_blueprint, url_prefix='/source')
    app.register_blueprint(stock_blueprint, url_prefix='/stock')

    @app.route('/')
    def home():
        my_stocks = [
            {"code": "301252", "name": "阿里云科技", "latest": "37.08", "change": "5.2%"},
            {"code": "603686", "name": "海尔之家", "latest": "13.17", "change": "10.03%"},
        ]
        my_stock_news = [
            "阿里云科技发布最新财报",
            "海尔之家连续三日涨停",
        ]

        user_avatar = session.get('avatar', '/static/default-avatar.png')  # 默认头像路径
        username = session.get('username', 'Guest')  # 未登录时显示默认用户名
        return render_template('index.html', my_stocks=my_stocks, my_stock_news=my_stock_news)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)