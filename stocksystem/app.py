from flask import Flask
from controller.user_controller import user_blueprint, test_db_connection
from model.user import db
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

    @app.route('/')
    def home():
        return " 路由访问 ：Go to /user/register or /user/login."

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
