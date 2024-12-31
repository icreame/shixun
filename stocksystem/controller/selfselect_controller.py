from flask import Blueprint, request, jsonify
from service.selfselect_service import SelfSelectService

selfselect_blueprint = Blueprint('selfselect', __name__)

# 添加自选股
@selfselect_blueprint.route('/add', methods=['POST'])
def add_self_select():
    data = request.json
    userid = data.get('userid')
    stockid = data.get('stockid')

    if not userid or not stockid:
        return jsonify({"success": False, "message": "userid 和 stockid 必须提供"}), 400

    result = SelfSelectService.add_self_select(userid, stockid)
    return jsonify(result)

# 获取某个用户的所有自选股
@selfselect_blueprint.route('/<int:userid>', methods=['GET'])
def get_user_self_selects(userid):
    selfselects = SelfSelectService.get_user_self_selects(userid)
    return jsonify({"success": True, "selfselects": selfselects})

# 删除自选股
@selfselect_blueprint.route('/remove', methods=['POST'])
def remove_self_select():
    data = request.json
    userid = data.get('userid')
    stockid = data.get('stockid')

    if not userid or not stockid:
        return jsonify({"success": False, "message": "userid 和 stockid 必须提供"}), 400

    result = SelfSelectService.remove_self_select(userid, stockid)
    return jsonify(result)
