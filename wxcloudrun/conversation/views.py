import json
import logging
import uuid

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from wxcloudrun.models import User, Conversation
from wxcloudrun.utils.decorators import token_required

# 创建日志器
logger = logging.getLogger('conversation')


@token_required
@require_http_methods(["POST"])
def conversation(request, user):
    """
    对话接口
    
    请求头:
        - Authorization: Bearer {token}
    请求参数:
        - sessionId: 会话ID
        - message: 用户消息
    返回:
        - replyId: 回复ID
        - reply: AI回复内容
        - suggestions: 建议输入
    """
    try:
        # 解析请求内容
        body = json.loads(request.body)
        session_id = body.get('sessionId', str(uuid.uuid4()))
        message = body.get('message')
        
        if not message:
            return JsonResponse({
                'code': -1,
                'errorMsg': '消息内容不能为空',
            }, status=400)

        # 获取会话历史或创建新会话
        conversation, created = Conversation.objects.get_or_create(
            user=user,
            session_id=session_id,
            defaults={'content': []}
        )
        
        # 追加用户消息到对话历史
        content = conversation.content
        if isinstance(content, str):
            content = json.loads(content)
        if not isinstance(content, list):
            content = []
        
        # 添加用户消息
        content.append({
            'role': 'user',
            'content': message,
            'timestamp': str(int(datetime.datetime.now().timestamp()))
        })
        
        # TODO: 调用阿里云百炼API获取回复
        # 这里为了演示，使用模拟回复
        reply_id = str(uuid.uuid4())
        mock_reply = "基于您的需求，我为您规划了一份3日游行程。第一天可以参观市中心的著名景点，第二天体验当地特色文化，第三天可以去周边自然风光区放松。您更倾向于哪种类型的住宿？"
        mock_suggestions = ["经济型酒店", "豪华度假村", "特色民宿", "添加更多景点"]
        
        # 添加AI回复
        content.append({
            'role': 'assistant',
            'replyId': reply_id,
            'content': mock_reply,
            'timestamp': str(int(datetime.datetime.now().timestamp()))
        })
        
        # 更新对话内容
        conversation.content = content
        conversation.save()
        
        return JsonResponse({
            'code': 0,
            'data': {
                'replyId': reply_id,
                'reply': mock_reply,
                'suggestions': mock_suggestions
            }
        })
        
    except Exception as e:
        logger.error(f"对话接口异常: {str(e)}")
        return JsonResponse({
            'code': -1,
            'errorMsg': f"处理失败: {str(e)}",
        }, status=500)