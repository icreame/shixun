import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用对象修改追踪
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:947400@localhost/stocksystem'

import os


class Config:
    # 基础配置
    # SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+mysqlconnector://root:947400@localhost/stocksystem' # 配置本地的数据库路径
    )


# 开发，测试，生产环境创建不同的配置类
class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = ''