from flask import Blueprint, request, jsonify
from flask_cors import CORS
from service.user_service import UserService

user_blueprint = Blueprint('user', __name__)
CORS(user_blueprint)  # 允许跨域请求


@user_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "需要用户名和密码"}), 400

    result = UserService.register(username, password)
    return jsonify(result)


@user_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "需要输入用户名和密码"}), 400

    result = UserService.login(username, password)
    return jsonify(result)


@user_blueprint.route('/user_info/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    """
    查看用户信息接口
    :param user_id: 用户ID，从URL路径中获取
    :return: 用户信息的JSON响应
    """
    if not user_id:
        return jsonify({"success": False, "message": "用户ID不能为空"}), 400

    result = UserService.get_user_info(user_id)
    return jsonify(result)


@user_blueprint.route('/update', methods=['POST'])
def update_user_info():
    data = request.json
    user_id = data.get('user_id')  # 从请求中获取用户ID
    new_info = data.get('new_info')  # 新的用户信息

    if not user_id or not new_info:
        return jsonify({"success": False, "message": "用户ID和更新信息不能为空"}), 400

    result = UserService.update_user_info(user_id, new_info)
    return jsonify(result)


@user_blueprint.route('/test_db', methods=['GET'])
def test_db_connection():
    # 调用服务层的数据库测试方法
    result = UserService.test_db_connection()
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500
