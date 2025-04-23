from django.urls import path
from wxcloudrun.share import views, comments

urlpatterns = [
    # 行程相关接口
    path('create', views.create_trip, name='create_trip'),
    path('list', views.get_trip_list, name='get_trip_list'),
    path('detail/<int:trip_id>', views.get_trip_detail, name='get_trip_detail'),
    path('like', views.like_trip, name='like_trip'),
    
    # 评论相关接口
    path('comment/add', comments.add_comment, name='add_comment'),
    path('comment/delete/<int:comment_id>', comments.delete_comment, name='delete_comment'),
]