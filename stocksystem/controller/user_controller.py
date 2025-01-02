from flask import Blueprint, request, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
from service.user_service import UserService

user_blueprint = Blueprint('user', __name__)
CORS(user_blueprint)  # 允许跨域请求


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    if request.method == 'POST':
        if not username or not password:
            return jsonify({"success": False, "message": "需要用户名和密码"}), 400

        result = UserService.register(username, password)
        if result['success']:
            return redirect(url_for('user.login'))  # 注册成功后跳转到登录页
        else:
            return render_template('register.html', message=result['message'], username_error=result.get('username_error'),
                                   password_error=result.get('password_error'))

    return render_template('register.html')


@user_blueprint.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        result = UserService.login(username, password)

        if result['success']:
            return redirect(url_for('user.get_user_info', user_id=result['userid']))
        else:
            return render_template('login.html', message=result['message'])
    return render_template('login.html')


@user_blueprint.route('/user_info/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    """
    查看用户信息接口
    :param user_id: 用户ID，从URL路径中获取
    :return: 用户信息的JSON响应
    """
    result = UserService.get_user_info(user_id)
    if result['success']:
        return render_template('user_info.html', user=result['data'])
    else:
        return render_template('user_info.html', message=result['message'])


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

