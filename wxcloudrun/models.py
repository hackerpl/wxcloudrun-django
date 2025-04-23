from datetime import datetime
from django.db import models


# 用户表
class User(models.Model):
    ROLE_CHOICES = [
        ('guest', '游客'),
        ('user', '普通用户'),
        ('member', '会员'),
    ]
    
    openid = models.CharField(max_length=100, unique=True, verbose_name='微信openid')
    nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name='昵称')
    avatar = models.URLField(max_length=255, null=True, blank=True, verbose_name='头像URL')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='角色')
    member_expire = models.DateTimeField(null=True, blank=True, verbose_name='会员过期时间')
    register_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    last_login = models.DateTimeField(auto_now=True, verbose_name='最后登录时间')

    def __str__(self):
        return self.nickname or self.openid

    class Meta:
        db_table = 'Users'
        verbose_name = '用户'
        verbose_name_plural = '用户'


# 对话记录表
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    session_id = models.CharField(max_length=100, verbose_name='会话标识')
    content = models.JSONField(default=dict, verbose_name='对话内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_update = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    def __str__(self):
        return f'{self.user.nickname or self.user.openid} - {self.session_id}'

    class Meta:
        db_table = 'Conversations'
        verbose_name = '对话记录'
        verbose_name_plural = '对话记录'
        indexes = [
            models.Index(fields=['user', 'session_id']),
        ]


# 行程分享表
class Trip(models.Model):
    DESIGN_STYLES = [
        ('constructivism', '构成主义'),
        ('minimalism', '极简主义'),
        ('modern', '大胆现代'),
        ('vintage', '优雅复古'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=255, verbose_name='行程标题')
    content = models.TextField(verbose_name='行程内容')
    design_style = models.CharField(max_length=50, choices=DESIGN_STYLES, verbose_name='设计风格')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    views = models.IntegerField(default=0, verbose_name='浏览量')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Trips'
        verbose_name = '行程分享'
        verbose_name_plural = '行程分享'
        ordering = ['-created_at']


# 评论表
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论用户')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='comments', verbose_name='行程')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f'{self.user.nickname or self.user.openid}: {self.content[:20]}'

    class Meta:
        db_table = 'Comments'
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']


# 保留原有的Counters模型以兼容现有代码
class Counters(models.Model):
    count = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.count)

    class Meta:
        db_table = 'Counters'
