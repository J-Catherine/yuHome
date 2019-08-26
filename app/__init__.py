from flask import Flask
from flask_bootstrap import Bootstrap  # 一个flask扩展，简化程序中集成bootstrap过程
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_pagedown import PageDown

# Bootstrap文件的基模板利用Jinja2的模板继承机制,让程序扩展一个具有基本页面结构的基模板
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

# 使用注册库中的方法生成 登陆管理对象login_manager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'log.login'  # 指明视图函数的位置


def create_app(config_name):
    # 定义工厂函数，在其中创建程序实例
    app = Flask(__name__)  # 创建
    app.config.from_object(config[config_name])
    # 配置。从config配置类中用from_object导入配置并选择配置对象
    bootstrap.init_app(app)  # 初始化
    moment.init_app(app)
    db.init_app(app)
    config[config_name].init_app(app)
    pagedown.init_app(app)
    login_manager.init_app(app)  # 管理对象login_manager初始化
    # 以上初始化
    
    # 从当前文件夹中的main入导main作为main蓝本
    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # 扩展main以外的app.log
    from .log import log as log_blueprint
    app.register_blueprint(log_blueprint, url_prefix='/log')
    
    from .notebook import notebook as notebook_blueprint
    app.register_blueprint(notebook_blueprint, url_prefix='/notebook')
    
    return app
