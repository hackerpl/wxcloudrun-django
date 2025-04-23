import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.paginator import Paginator

from wxcloudrun.models import Trip, Comment
from wxcloudrun.utils.decorators import token_required

# 创建日志器
logger = logging.getLogger('share')


@token_required
@require_http_methods(["POST"])
def create_trip(request, user):
    """
    创建行程接口
    
    请求参数:
        - title: 行程标题
        - content: 行程内容
        - design_style: 设计风格
    返回:
        - tripId: 行程ID
    """
    try:
        # 解析请求内容
        body = json.loads(request.body)
        title = body.get('title')
        content = body.get('content')
        design_style = body.get('design_style')
        
        # 验证必填参数
        if not title:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程标题不能为空'
            }, status=400)
            
        if not content:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程内容不能为空'
            }, status=400)
        
        # 创建行程
        trip = Trip(
            user=user,
            title=title,
            content=content,
            design_style=design_style
        )
        trip.save()
        
        # 返回行程ID
        return JsonResponse({
            'code': 0,
            'data': {
                'tripId': trip.id
            }
        })
        
    except Exception as e:
        logger.error(f"创建行程异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"创建行程失败: {str(e)}",
        }, status=500)


@token_required
@require_http_methods(["GET"])
def get_trip_list(request, user):
    """
    获取行程列表接口
    
    请求参数:
        - page: 页码(可选，默认1)
        - page_size: 每页数量(可选，默认10)
        - mine: 是否只查看自己的行程(可选，默认0，表示查看所有)
    返回:
        - trips: 行程列表
        - total: 总行程数
        - page: 当前页码
        - page_size: 每页数量
    """
    try:
        page = int(request.GET.get('page', '1'))
        page_size = int(request.GET.get('page_size', '10'))
        mine = int(request.GET.get('mine', '0'))
        
        # 过滤条件
        if mine:
            trips = Trip.objects.filter(user=user)
        else:
            trips = Trip.objects.all()
        
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
        logger.error(f"获取行程列表异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"获取行程列表失败: {str(e)}",
        }, status=500)


@require_http_methods(["GET"])
def get_trip_detail(request, trip_id):
    """
    获取行程详情接口
    
    路径参数:
        - trip_id: 行程ID
    返回:
        - trip: 行程详情
    """
    try:
        trip_id = int(trip_id)
        
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'errorMsg': '行程不存在'
            }, status=404)
        
        # 增加浏览量
        trip.views += 1
        trip.save(update_fields=['views'])
        
        # 构建返回数据
        trip_data = {
            'id': trip.id,
            'title': trip.title,
            'content': trip.content,
            'userId': trip.user_id,
            'nickname': trip.user.nickname,
            'avatar': trip.user.avatar,
            'designStyle': trip.design_style,
            'createdAt': trip.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'views': trip.views,
            'likes': trip.likes,
            'comments': []
        }
        
        # 获取评论
        comments = Comment.objects.filter(trip=trip).order_by('-created_at')
        for comment in comments:
            trip_data['comments'].append({
                'id': comment.id,
                'content': comment.content,
                'userId': comment.user_id,
                'nickname': comment.user.nickname,
                'avatar': comment.user.avatar,
                'createdAt': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'code': 0,
            'data': {
                'trip': trip_data
            }
        })
        
    except Exception as e:
        logger.error(f"获取行程详情异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"获取行程详情失败: {str(e)}",
        }, status=500)


@token_required
@require_http_methods(["POST"])
def like_trip(request, user):
    """
    点赞行程接口
    
    请求参数:
        - trip_id: 行程ID
    返回:
        - likes: 当前点赞数
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
        
        # 增加点赞数
        trip.likes += 1
        trip.save(update_fields=['likes'])
        
        return JsonResponse({
            'code': 0,
            'data': {
                'likes': trip.likes
            }
        })
        
    except Exception as e:
        logger.error(f"点赞行程异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"点赞行程失败: {str(e)}",
        }, status=500)