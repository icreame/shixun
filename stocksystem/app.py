from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, session, g, jsonify,request
from controller.user_controller import user_blueprint, test_db_connection
from controller.industry_controller import industry_blueprint
from controller.news_controller import news_blueprint
from controller.selfselect_controller import selfselect_blueprint
from controller.sentiment_controller import sentiment_blueprint
from controller.source_controller import source_blueprint
from service.stock_service import StockService
from model.__init__ import db
from config import Config
from stocksystem.controller.stock_controller import stock_blueprint
from stocksystem.service.industry_service import IndustryService
from stocksystem.service.news_service import NewsService
from math import ceil

from stocksystem.service.sentiment_service import SentimentService
from stocksystem.service.source_service import SourceService


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

    # 启动调度器
    scheduler = BackgroundScheduler()
    scheduler.add_job(StockService.update_data, 'interval', weeks=4)  # 每4周（一个月）更新一次数据
    scheduler.start()

    @app.before_request
    def before_request():

        cached_data1 = StockService.loadtop10_data_from_cache()

        # 如果没有数据或数据过期，更新数据
        if  cached_data1 is None or StockService.is_data_expired():
            StockService.update_data()  # 仅在数据过期时更新

        # 将 stock_data 存储在 g 对象中，以便在视图中使用
        g.top10_data = StockService.loadtop10_data_from_cache()
    @app.route('/')
    def home():
        industries=IndustryService.get_all_industries()
        sources=SourceService.get_all_sources()
        sentiments=SentimentService.get_all_sentiments()

        # 检查会话中是否存在userid
        if 'userid' in session:  # 判断session中是否有userid
            userid = session['userid']  # 从会话中获取userid
        else:

            userid = None

        my_stocks = [
            {"code": "301252", "name": "阿里云科技", "latest": "37.08", "change": "5.2%"},
            {"code": "603686", "name": "海尔之家", "latest": "13.17", "change": "10.03%"},
        ]
        per_page = 5
        page = request.args.get('page', 1, type=int)  # 获取当前页，默认为1

        # 获取新闻数据，限制每页的条数
        news_data = NewsService.get_all_news(page, per_page)
        news_list = news_data["data"]

        # 获取总新闻数，用于计算总页数
        total_news = news_data['total']
        total_pages = ceil(total_news / per_page)

        # top10_data = StockService.get_top10_stocks()

        # 分页显示范围：当前页前后各两页
        page_range = list(range(max(1, page - 2), min(total_pages + 1, page + 3)))

        # 如果总页数超过一定范围，显示“省略号”
        if page_range[0] > 1:
            page_range = [1, '...'] + page_range
        if page_range[-1] < total_pages:
            page_range = page_range + ['...'] + [total_pages]

        return render_template('index.html', userid=userid,my_stocks=my_stocks,
                               stock_news=news_list,top10_data=g.top10_data,total_pages=total_pages,
                               current_page=page,page_range=page_range,
                               industries=industries,
                               sources=sources,
                               sentiments=sentiments,
                               threshold=7,
                               total_news=total_news
                               )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


