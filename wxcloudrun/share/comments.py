import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction

from wxcloudrun.models import Trip, Comment
from wxcloudrun.utils.decorators import token_required

# 创建日志器
logger = logging.getLogger('comments')


@token_required
@require_http_methods(["POST"])
def add_comment(request, user):
    """
    添加评论接口
    
    请求参数:
        - trip_id: 行程ID
        - content: 评论内容
    返回:
        - commentId: 评论ID
    """
    try:
        # 解析请求内容
        body = json.loads(request.body)
        trip_id = body.get('trip_id')
        content = body.get('content')
        
        # 验证必填参数
        if not trip_id:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程ID不能为空'
            }, status=400)
            
        if not content:
            return JsonResponse({
                'code': -1,
                'errorMsg': '评论内容不能为空'
            }, status=400)
        
        # 验证行程是否存在
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程不存在'
            }, status=404)
        
        # 创建评论
        with transaction.atomic():
            comment = Comment(
                user=user,
                trip=trip,
                content=content
            )
            comment.save()
        
        # 返回评论ID
        return JsonResponse({
            'code': 0,
            'data': {
                'commentId': comment.id,
                'nickname': user.nickname,
                'avatar': user.avatar,
                'createdAt': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        logger.error(f"添加评论异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"添加评论失败: {str(e)}",
        }, status=500)


@token_required
@require_http_methods(["DELETE"])
def delete_comment(request, comment_id, user):
    """
    删除评论接口
    
    路径参数:
        - comment_id: 评论ID
    返回:
        - success: 是否成功
    """
    try:
        # 查找评论
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'errorMsg': '评论不存在'
            }, status=404)
        
        # 验证权限（只能删除自己的评论，管理员可以删除任何评论）
        if comment.user_id != user.id and user.role != 'admin':
            return JsonResponse({
                'code': -2,
                'errorMsg': '无权限删除此评论'
            }, status=403)
        
        # 删除评论
        comment.delete()
        
        return JsonResponse({
            'code': 0,
            'data': {
                'success': True
            }
        })
        
    except Exception as e:
        logger.error(f"删除评论异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"删除评论失败: {str(e)}",
        }, status=500)