from django.urls import path
from wxcloudrun.auth import views

urlpatterns = [
    # 用户登录接口
    path('login', views.login, name='login'),
]