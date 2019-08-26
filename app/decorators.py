from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


# 实现了两个修饰器
# 检查常规权限
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                # 如果用户不具有指定权限,则返 回 403 错误码,即 HTTP“禁止”错误。
                abort(403)
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


# 检查管理员权限
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
