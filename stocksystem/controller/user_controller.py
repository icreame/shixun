from flask import Blueprint, request, jsonify, render_template, request, redirect, url_for, session, flash
from flask_cors import CORS
from stocksystem.service.user_service import UserService

user_blueprint = Blueprint('user', __name__)
CORS(user_blueprint)  # 允许跨域请求


@user_blueprint.route('/register', methods=['GET','POST'])
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
            return redirect(url_for('home', user_id=result['userid']))
        else:
            return render_template('login.html', message=result['message'])
    return render_template('login.html')

@user_blueprint.route('/logout', methods=['GET'])
def logout():
    # 注销逻辑
    session.clear()
    return redirect(url_for('home'))


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
    userid = request.args.get('user_id', type=int)
    username = request.form.get('username')
    gender=request.form.get('gender')
    profession=request.form.get('profession')
    phone=request.form.get('phone')
    email=request.form.get('email')
    address=request.form.get('address')

    if not username:
        return jsonify({"success": False, "message": "用户名不能为空"}), 400
    result = UserService.update_user_info(userid, username, gender, profession, phone, email, address)
    if result['success']:
        return redirect(url_for('user.get_user_info',user_id=userid))  # 更新成功后跳转到个人信息页


@user_blueprint.route('/test_db', methods=['GET'])
def test_db_connection():
    # 调用服务层的数据库测试方法
    result = UserService.test_db_connection()
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500

@user_blueprint.route('/update/change_password', methods=['POST'])
def change_password():
    userid = request.args.get('user_id', type=int)
    old_password=request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password=request.form.get('confirm_password')
    result=UserService.change_password(userid, old_password, new_password,confirm_password)
    if result["success"]:
        return redirect(url_for('user.get_user_info',user_id=userid))
    else:
        return jsonify(result)
