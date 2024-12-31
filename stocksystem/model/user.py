from datetime import datetime
from model.__init__ import db


class User(db.Model):
    __tablename__ = 'user'

    # 数据库字段定义
    user_id = db.Column("userid", db.Integer, primary_key=True, autoincrement=True)  # 数据库字段 userid
    username = db.Column("username", db.String(50), unique=True, nullable=False)  # 数据库字段 username
    password = db.Column("password", db.String(255), nullable=False)  # 数据库字段 password
    phone = db.Column("phone", db.String(13))   # 数据库字段 phone
    email = db.Column("email",db.String(50))    # 数据库字段 email
    address = db.Column("address", db.String(50))   # 数据库字段 address
    gender = db.Column("gender", db.String(5))  # 数据库字段 gender
    profession = db.Column("profession",db.String(20))  # 数据库字段 profession
    registration_date = db.Column("registrationdate", db.Date, nullable=False,
                                  default=datetime.utcnow)  # 数据库字段 registrationdate
    permission_level = db.Column("permissionlevel", db.Integer, nullable=False)  # 数据库字段 permissionlevel

    def __init__(self, username, password, phone=None, email=None, address=None, gender=None, profession=None, is_admin=False):
        self.username = username
        self.password = password
        self.phone=phone
        self.address = address
        self.gender = gender
        self.email = email
        self.profession = profession
        self.RegistrationDate = datetime.utcnow()
        self.permission_level = 10 if is_admin else 1  # 10 表示管理员，1 表示普通用户