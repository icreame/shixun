from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from service.stock_service import StockService
from apscheduler.schedulers.background import BackgroundScheduler
from flask import g

stock_blueprint = Blueprint('stock', __name__)
CORS(stock_blueprint)  # 允许跨域请求


@stock_blueprint.route('/create', methods=['POST'])
def create_stock():
    """
    创建股票
    """
    data = request.json
    stockname = data.get('stockname')
    stockprice = data.get('stockprice')
    industryid = data.get('industryid')

    if not stockname or not stockprice or not industryid:
        return jsonify({"success": False, "message": "股票名称、价格和行业ID不能为空"}), 400

    result = StockService.create_stock(stockname, stockprice, industryid)
    return jsonify(result)


@stock_blueprint.route('/update', methods=['PUT'])
def update_stock():
    """
    更新股票信息
    """
    data = request.json
    stock_id = data.get('stock_id')
    stockname = data.get('stockname')
    stockprice = data.get('stockprice')
    industryid = data.get('industryid')

    if not stock_id:
        return jsonify({"success": False, "message": "股票ID不能为空"}), 400

    result = StockService.update_stock(stock_id, stockname, stockprice, industryid)
    return jsonify(result)


@stock_blueprint.route('/delete/<int:stockid>', methods=['DELETE'])
def delete_stock(stockid):
    """
    删除股票
    """
    result = StockService.delete_industry(stockid)
    return jsonify(result)


@stock_blueprint.route('/all', methods=['GET'])
def get_all_stocks():
    """
    获取所有股票信息
    """
    result = StockService.get_all_stocks()
    return jsonify(result)


@stock_blueprint.route('/get/<int:stock_id>', methods=['GET'])
def get_stock_by_id(stock_id):
    """
    根据股票ID获取股票信息
    """
    result = StockService.get_stock_by_id(stock_id)
    return jsonify(result)


@stock_blueprint.route('/get_by_industry/<int:industry_id>', methods=['GET'])
def get_stocks_by_industry(industry_id):
    """
    根据行业ID获取股票信息
    """
    result = StockService.get_stocks_by_industry(industry_id)
    return jsonify(result)

@stock_blueprint.before_request
def before_request():
    cached_data = StockService.load_data_from_cache()

    # 如果没有数据或数据过期，更新数据
    if cached_data is  None or StockService.is_data_expired():
        StockService.update_data()  # 仅在数据过期时更新

    # 将 stock_data 存储在 g 对象中，以便在视图中使用
    g.stock_data = StockService.load_data_from_cache()

@stock_blueprint.route('/', methods=['GET'])
def stocks_view():
    return render_template('stocks_view.html', data=g.stock_data)

@stock_blueprint.route('/mystock', methods=['GET'])
def mystock():
    user_id = session.get('userid')
    if not user_id:
        return redirect(url_for('user.login'))


    news_list = [
        {
            "title": "瑞达期货：铁矿石短线行情波动较大，建议日内短线交易",
            "source": "国家发展改革委员会",
            "date": "9分钟前",
            "tags": ["证券期货", "客户投诉", "财经"],
            "summary": "当前国内铁矿石价格已有再度回升，同期华东、华中及其他地区部分钢厂调整临时限价措施，市场监管总局高度关注铁矿石的价格变化。",
            "sentiment": "中性"
        },
        {
            "title": "滑向世界的“坡弯”",
            "source": "ZAKER兰州",
            "date": "14分钟前",
            "tags": ["体育产业", "竞技比赛", "教育"],
            "summary": "首都滑雪爱好者使用的某选手曾获世界冠军的器材。这种跨时代产品帮助中国队提升技术，受到热烈追捧。",
            "sentiment": "正面"
        }
    ]
    my_stocks = [
        {"code": "301252", "name": "阿里云科技", "latest": "37.08", "change": "5.2%"},
        {"code": "603686", "name": "海尔之家", "latest": "13.17", "change": "10.03%"},
    ]

    # 搜索条件
    search_query = request.args.get('search_query', '').strip()
    page = int(request.args.get('page', 1))

    search_results = None  # 初始化为空
    stocks_per_page = 10  # 每页显示 10 条

    if search_query:  # 如果存在搜索条件
        # 分页查询与搜索逻辑
        search_results = StockService.search_stocks(search_query, page=stocks_per_page)

    # 调用 Service 层获取搜索结果

    print("Search Query:", search_query)
    print("Search Results:", search_results)

    return render_template('mystock.html', page=page,search_query=search_query, search_results=search_results,
                           userid=user_id, s=search_results, stock_news=news_list,my_stocks=my_stocks)


@stock_blueprint.route('/get_index_data', methods=['GET'])
def index_data():
    result=StockService.get_index_data()
    print(result)
    return jsonify(result)

@stock_blueprint.route('/get_limit_stocks',methods=['GET'])
def limit_stocks():
    result=StockService.get_limit_stocks()
    return jsonify(result)