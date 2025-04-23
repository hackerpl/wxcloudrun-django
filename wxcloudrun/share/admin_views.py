import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.paginator import Paginator

from wxcloudrun.models import Trip, Comment
from wxcloudrun.utils.decorators import token_required, role_required

# 创建日志器
logger = logging.getLogger('share')


@token_required
@role_required(['admin'])
@require_http_methods(["GET"])
def get_featured_trips(request, user):
    """
    获取推荐行程列表接口
    
    请求参数:
        - page: 页码(可选，默认1)
        - page_size: 每页数量(可选，默认10)
    返回:
        - trips: 行程列表
        - total: 总行程数
        - page: 当前页码
        - page_size: 每页数量
    """
    try:
        page = int(request.GET.get('page', '1'))
        page_size = int(request.GET.get('page_size', '10'))
        
        # 获取所有推荐行程
        trips = Trip.objects.filter(is_featured=True).order_by('-created_at')
        
        # 分页
        paginator = Paginator(trips, page_size)
        current_page = paginator.page(page)
        
        # 构建返回数据
        trips_data = []
        for trip in current_page.object_list:
            trips_data.append({
                'id': trip.id,
                'title': trip.title,
                'userId': trip.user_id,
                'nickname': trip.user.nickname,
                'avatar': trip.user.avatar,
                'designStyle': trip.design_style,
                'createdAt': trip.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'views': trip.views,
                'likes': trip.likes,
                'commentCount': trip.comments.count()
            })
        
        return JsonResponse({
            'code': 0,
            'data': {
                'trips': trips_data,
                'total': paginator.count,
                'page': page,
                'page_size': page_size
            }
        })
        
    except Exception as e:
        logger.error(f"获取推荐行程列表异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"获取推荐行程列表失败: {str(e)}",
        }, status=500)


@token_required
@role_required(['admin'])
@require_http_methods(["POST"])
def feature_trip(request, user):
    """
    管理员推荐行程接口
    
    请求参数:
        - trip_id: 行程ID
        - is_featured: 是否推荐(0/1)
    返回:
        - success: 是否成功
    """
    try:
        # 解析请求内容
        body = json.loads(request.body)
        trip_id = body.get('trip_id')
        is_featured = body.get('is_featured', 0)
        
        if not trip_id:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程ID不能为空'
            }, status=400)
        
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程不存在'
            }, status=404)
        
        # 更新行程推荐状态
        trip.is_featured = bool(is_featured)
        trip.save(update_fields=['is_featured'])
        
        return JsonResponse({
            'code': 0,
            'data': {
                'success': True
            }
        })
        
    except Exception as e:
        logger.error(f"推荐行程异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"推荐行程失败: {str(e)}",
        }, status=500)


@token_required
@role_required(['admin'])
@require_http_methods(["POST"])
def delete_trip(request, user):
    """
    管理员删除行程接口
    
    请求参数:
        - trip_id: 行程ID
    返回:
        - success: 是否成功
    """
    try:
        # 解析请求内容
        body = json.loads(request.body)
        trip_id = body.get('trip_id')
        
        if not trip_id:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程ID不能为空'
            }, status=400)
        
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程不存在'
            }, status=404)
        
        # 删除行程（会级联删除关联的评论）
        with transaction.atomic():
            trip.delete()
        
        return JsonResponse({
            'code': 0,
            'data': {
                'success': True
            }
        })
        
    except Exception as e:
        logger.error(f"删除行程异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"删除行程失败: {str(e)}",
        }, status=500)