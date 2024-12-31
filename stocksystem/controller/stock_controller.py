from flask import Blueprint, request, jsonify
from flask_cors import CORS
from service.stock_service import StockService

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


@stock_blueprint.route('/update', methods=['POST'])
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


@stock_blueprint.route('/delete', methods=['POST'])
def delete_stock():
    """
    删除股票
    """
    data = request.json
    stock_id = data.get('stock_id')

    if not stock_id:
        return jsonify({"success": False, "message": "股票ID不能为空"}), 400

    result = StockService.delete_stock(stock_id)
    return jsonify(result)


@stock_blueprint.route('/get_all', methods=['GET'])
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
