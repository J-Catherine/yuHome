from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)


@main.app_context_processor
# 上下文处理器, Permission 类为所有位定义了常量以便于获取
def inject_permissions():
    return dict(Permission=Permission)


from . import views, errors
