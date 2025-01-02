from flask import Flask
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
        return " 路由访问 ：Go to /user/register or /user/login."

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)