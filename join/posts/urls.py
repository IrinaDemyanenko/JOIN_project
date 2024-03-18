from django.urls import path
from . import views

app_name = 'posts'  # переменная namespase

urlpatterns = [
    path('', views.index, name='index'),
    path('group/', views.all_groups, name='all_groups'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
]
