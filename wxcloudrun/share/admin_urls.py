from django.urls import path
from wxcloudrun.share import admin_views

urlpatterns = [
    # 管理员行程管理接口
    path('feature', admin_views.feature_trip, name='feature_trip'),
    path('delete', admin_views.delete_trip, name='delete_trip'),
    path('featured-list', admin_views.get_featured_trips, name='get_featured_trips'),
]