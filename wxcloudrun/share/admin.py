from django.contrib import admin
from wxcloudrun.models import Trip, Comment


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'design_style', 'created_at', 'views', 'likes')
    list_filter = ('design_style', 'created_at')
    search_fields = ('title', 'content', 'user__nickname')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'trip', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__nickname', 'trip__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'