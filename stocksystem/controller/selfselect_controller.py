from flask import Blueprint, request, jsonify
from service.selfselect_service import SelfSelectService

from stocksystem.service.stock_service import StockService

selfselect_blueprint = Blueprint('selfselect', __name__)


@selfselect_blueprint.route('/add', methods=['POST'])
def add_self_select():
    """
    添加自选股
    """
    data = request.json
    userid = data.get('userid')
    stockcode = data.get('stockid')

    if not userid or not stockcode:
        return jsonify({"success": False, "message": "userid 和 stockcode 必须提供"}), 400

    stockid=StockService.get_stockid_by_stockcode(stockcode)
    result = SelfSelectService.add_self_select(userid, stockid)
    # 返回结果
    if result['success']:
        return jsonify({"success": True, "message": result['message']})
    else:
        return jsonify({"success": False, "message": result['message']}), 400



@selfselect_blueprint.route('/<int:userid>', methods=['GET'])
def get_user_self_selects(userid):
    """
    获取某用户的自选股
    """
    selfselect=SelfSelectService()

    selfselects = selfselect.get_user_self_selects(userid)
    return jsonify({"success": True, "selfselects": selfselects})


@selfselect_blueprint.route('/remove', methods=['GEt','POST'])
def remove_self_select():
    """
    移除自选股
    """
    data = request.json
    userid = data.get('userid')
    stockid = data.get('stockid')

    if not userid or not stockid:
        return jsonify({"success": False, "message": "userid 和 stockid 必须提供"}), 400

    result = SelfSelectService.remove_self_select(userid, stockid)
    return jsonify(result)

@selfselect_blueprint.route('news/<int:userid>', methods=['GET'])
def get_selfselect_news(userid):
    """
    获取自选股新闻
    :param userid:
    :return:
    """
    result=SelfSelectService.get_selfselect_news(userid)
    return jsonify(result)

