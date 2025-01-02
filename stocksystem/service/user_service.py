from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from model.user import User, db
from sqlalchemy.sql import text

class UserService:
    @staticmethod
    def register(username, password):
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return {"success": False, "message": "用户已存在"}

        # 加密密码并创建用户（暂未使用）
        # hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=password)

        # 添加到数据库
        try:
            db.session.add(new_user)
            db.session.commit()
            return {"success": True, "message": "用户注册成功", "UserID": new_user.user_id}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"用户注册失败: {str(e)}"}

    @staticmethod
    def login(username, password):
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return {"success": False, "message": "未找到用户"}

        # 验证密码（暂未使用）
        # if not check_password_hash(user.password, password):
        #     return {"success": False, "message": "密码不正确"}
        # 验证明文密码
        if user.password != password:  # 直接比对用户输入的密码和数据库中的密码
            return {"success": False, "message": "密码不正确","userid":user.user_id}
        session['logged_in'] = True
        session['username'] = user.username
        session['userid'] = user.user_id

        return {"success": True, "message": "登录成功","userid":user.user_id}

    @staticmethod
    def get_user_info(user_id):
        """
        获取用户信息
        :param user_id: 用户ID
        :return: 用户信息字典
        """
        user = User.query.get(user_id)
        if not user:
            return {"success": False, "message": "用户不存在"}

        # 返回用户信息
        user_info = {
            "user_id": user.user_id,
            "username": user.username,
            "phone":user.phone,
            "email":user.email,
            "address":user.address,
            "gender":user.gender,
            "profession":user.profession,
            "registration_date": user.registration_date,
            "permission_level": user.permission_level
        }
        return {"success": True, "data": user_info}


    @staticmethod
    def update_user_info(user_id, new_info):
        """
        更新用户信息
        :param user_id: 用户ID
        :param new_info: 字典类型，包含要更新的字段和值
        :return: 操作结果字典
        """
        user = User.query.get(user_id)
        if not user:
            return {"success": False, "message": "用户不存在"}

        # 遍历 new_info，更新对应字段
        for key, value in new_info.items():
            if hasattr(user, key):  # 确保 User 模型具有该属性
                setattr(user, key, value)

        try:
            db.session.commit()
            return {"success": True, "message": "信息更新成功"}
        except Exception as e:
            db.session.rollback()  # 回滚事务以防止数据损坏
            return {"success": False, "message": f"信息更新失败: {str(e)}"}

    # 用于测试数据库是否连接成功
    @staticmethod
    def test_db_connection():
        """
        测试数据库连接
        :return: 测试结果字典
        """
        try:
            db.session.execute(text('SELECT 1'))  # 测试数据库连接
            return {"success": True, "message": "数据库连接成功"}
        except Exception as e:
            return {"success": False, "message": f"数据库连接失败: {str(e)}"}
