import jwt
import logging
import functools

from django.http import JsonResponse
from wxcloudrun.models import User

# JWT密钥，实际应用中应该放在settings中
JWT_SECRET = 'ff_travel_jwt_secret'

logger = logging.getLogger('auth')


def token_required(view_func):
    """
    用于验证JWT令牌的装饰器
    成功后会将当前用户对象传递给视图函数
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 获取Authorization头
        auth_header = request.headers.get('Authorization', '')
        
        # 检查头格式
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'code': -2,
                'errorMsg': '未授权访问'
            }, status=401)
        
        # 提取token
        token = auth_header[7:]
        
        try:
            # 验证token
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # 获取用户
            user = User.objects.get(id=user_id)
            
            # 调用视图函数，附加用户参数
            return view_func(request, user=user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                'code': -2,
                'errorMsg': '登录已过期，请重新登录'
            }, status=401)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return JsonResponse({
                'code': -2,
                'errorMsg': '无效的身份令牌'
            }, status=401)
        except Exception as e:
            logger.error(f"Token验证异常: {str(e)}")
            return JsonResponse({
                'code': -1,
                'errorMsg': '服务器内部错误'
            }, status=500)
    
    return wrapper


def role_required(allowed_roles):
    """
    用于验证用户角色权限的装饰器
    需要与token_required装饰器一起使用
    
    参数:
        allowed_roles: 允许访问的角色列表，如['admin', 'member']
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, user, *args, **kwargs):
            # 验证用户角色
            if user.role not in allowed_roles:
                return JsonResponse({
                    'code': -3,
                    'errorMsg': '没有权限执行此操作'
                }, status=403)
            
            # 调用视图函数
            return view_func(request, user=user, *args, **kwargs)
            
        return wrapper
    return decorator