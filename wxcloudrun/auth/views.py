import json
import logging
import time
import jwt

from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods

from wxcloudrun.models import User

# 创建日志器
logger = logging.getLogger('auth')

# JWT密钥，实际应用中应该放在settings中，这里为了演示直接写在代码中
JWT_SECRET = 'ff_travel_jwt_secret'

# JWT过期时间设置为30天
JWT_EXPIRE_DAYS = 30


@require_http_methods(["POST"])
def login(request):
    """
    微信授权登录接口
    
    请求参数:
        - code: 微信登录code
        - userInfo: 用户信息
    返回:
        - token: 登录token
        - userId: 用户ID
        - role: 用户角色
    """
    try:
        # 解析请求内容
        body = json.loads(request.body)
        code = body.get('code')
        user_info = body.get('userInfo', {})
        
        if not code:
            return JsonResponse({
                'code': -1,
                'errorMsg': '缺少微信登录code',
            }, status=400)

        # TODO: 实际环境中，需要调用微信开放平台接口换取用户openid
        # 这里为了演示，假设已经获取到了openid
        openid = f"simulated_openid_{code}"  # 实际场景应通过微信API获取
        
        # 获取或创建用户
        try:
            user = User.objects.get(openid=openid)
            # 更新用户信息
            if user_info:
                user.nickname = user_info.get('nickName', user.nickname)
                user.avatar = user_info.get('avatarUrl', user.avatar)
                user.save(update_fields=['nickname', 'avatar', 'last_login'])
        except User.DoesNotExist:
            # 创建新用户
            user = User(
                openid=openid,
                nickname=user_info.get('nickName'),
                avatar=user_info.get('avatarUrl'),
                role='user',  # 默认为普通用户
            )
            user.save()
        
        # 生成JWT Token
        token_payload = {
            'user_id': user.id,
            'openid': user.openid,
            'role': user.role,
            'exp': int(time.time()) + 60 * 60 * 24 * JWT_EXPIRE_DAYS,  # 30天过期
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
        
        # 返回用户信息
        return JsonResponse({
            'code': 0,
            'data': {
                'token': token,
                'userId': user.id,
                'role': user.role,
            }
        })
        
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"登录失败: {str(e)}",
        }, status=500)