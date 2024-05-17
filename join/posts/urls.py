from django.urls import path
from . import views

app_name = 'posts'  # переменная namespase

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('group/', views.all_groups, name='all_groups'),
    path('profile/<str:username>/', views.profile, name='profile'),
    # Django ожидает строковое значение и преобразует его
    # в представление — переменную username.
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Django ожидает целочисленное значение и преобразует его
    # в представление — переменную post_id.
    path('create/', views.post_create, name='post_create'),
]
