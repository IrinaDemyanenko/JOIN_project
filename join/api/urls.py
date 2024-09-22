from django.urls import path, include
from rest_framework.authtoken import views

from api.api_view import (APIPost, APIPostDetail,
                       APIGenericPostList, APIGenericPostDetail,
                       PostViewSet, GroupViewSet, CommentViewSet)
from rest_framework.routers import DefaultRouter

# создаём роутер
router = DefaultRouter()
# регистрируем созданный ViewSet
#api/v1/posts/ (GET, POST): получаем список всех постов или создаём новый пост
#api/v1/posts/{post_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем пост по id
router.register(r'posts', PostViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'^posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comment')



urlpatterns = [
    # получение простого токена по логину и паролю
    path('api/v1/api-token-auth/', views.obtain_auth_token),
    # path('api/v1/posts/<int:pk>', APIGenericPostDetail.as_view(), name='api_post_detail'),
    # path('api/v1/posts/', APIGenericPostList.as_view(), name='api_posts'),
    path('api/v1/', include(router.urls))
]
