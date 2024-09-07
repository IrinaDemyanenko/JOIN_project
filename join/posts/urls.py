from django.urls import path
from . import views
from .api_view import APIPost, APIPostDetail, APIGenericPostList, APIGenericPostDetail

app_name = 'posts'  # переменная namespase

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('group/', views.all_groups, name='all_groups'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('profile/<str:username>/', views.profile, name='profile'),
    # Django ожидает строковое значение и преобразует его
    # в представление — переменную username.
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Django ожидает целочисленное значение и преобразует его
    # в представление — переменную post_id.
    path('create/', views.post_create, name='post_create'),
    path('follow/', views.follow_index, name='follow_index'),
    path('api/v1/posts/<int:pk>', APIGenericPostDetail.as_view(), name='api_post_detail'),
    path('api/v1/posts/', APIGenericPostList.as_view(), name='api_posts'),
]
