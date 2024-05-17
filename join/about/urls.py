from django.urls import path
from . import views


app_name = 'about'
# Строка app_name = 'about' — обязательна. Без неё namespace не сработает.

urlpatterns = [
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    path('tech/', views.AboutTechView.as_view(), name='tech')
]
