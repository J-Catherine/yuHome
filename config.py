import os

#获得当前文件的绝对路径，用于索引数据库
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'JWKR is a queen!'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or "JWKR@123.com"
    FLASKY_POSTS_PER_PAGE = 15
    FLASKY_COMMENTS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass

#设置是一种类，不同版本的设置继承于初始版
#两种不同版本的设置，主要是数据库文件的位置不同
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

class NewMySQLConfig(Config):
    password = os.environ.get('DATABASE_PASSWORD') or "password"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:'+ password + '@localhost:3306/family'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

#用于选择不同配置的字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': NewMySQLConfig,
    'mysql': NewMySQLConfig
}
