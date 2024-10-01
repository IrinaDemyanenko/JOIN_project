from django.urls import path, include
from rest_framework.authtoken import views

from api.api_view import (APIPost, APIPostDetail,
                       APIGenericPostList, APIGenericPostDetail, FollowViewSet,
                       PostViewSet, GroupViewSet, CommentViewSet)
from rest_framework.routers import DefaultRouter


app_name = 'api'  # у прилож. должно быть имя, далее исп его в namespace

# создаём роутер
router = DefaultRouter()
# регистрируем созданный ViewSet
#api/v1/posts/ (GET, POST): получаем список всех постов или создаём новый пост
#api/v1/posts/{post_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем пост по id
router.register(r'posts', PostViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'^posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comment')
router.register(r'follow', FollowViewSet, basename='follow')



urlpatterns = [
    # получение простого токена по логину и паролю
    #path('api/v1/api-token-auth/', views.obtain_auth_token),
    # path('api/v1/posts/<int:pk>', APIGenericPostDetail.as_view(), name='api_post_detail'),
    # path('api/v1/posts/', APIGenericPostList.as_view(), name='api_posts'),
    # получение токена JWT
    # Djoser создаст набор необходимых эндпоинтов.
    # базовые, для управления пользователями в Django:
    path('auth/', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls))
]
