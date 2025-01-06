from flask import Blueprint, request, jsonify
from service.selfselect_service import SelfSelectService

selfselect_blueprint = Blueprint('selfselect', __name__)


@selfselect_blueprint.route('/add', methods=['POST'])
def add_self_select():
    """
    添加自选股
    """
    data = request.json
    userid = data.get('userid')
    stockid = data.get('stockid')

    if not userid or not stockid:
        return jsonify({"success": False, "message": "userid 和 stockid 必须提供"}), 400

    result = SelfSelectService.add_self_select(userid, stockid)
    return jsonify(result)


@selfselect_blueprint.route('/<int:userid>', methods=['GET'])
def get_user_self_selects(userid):
    """
    获取某用户的自选股
    """

    selfselects = SelfSelectService.get_user_self_selects(userid)
    return jsonify({"success": True, "selfselects": selfselects})


@selfselect_blueprint.route('/remove', methods=['POST'])
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
