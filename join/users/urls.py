from django.contrib.auth.views import (LogoutView, LoginView,
                                       PasswordResetView,
                                       PasswordChangeView,
                                       PasswordChangeDoneView,
                                       PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from django.urls import path
from . import views


app_name = 'users'  # у прилож. должно быть имя, далее исп его в namespace

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    # Прямо в описании обработчика укажем шаблон,
    # который должен применяться для отображения возвращаемой страницы.
    # Да, во view-классах так можно! Как их не полюбить.
    # Теперь при обработке запроса auth/logout/ будет использоваться
    # контент, генерируемый LogoutView, а шаблон будет взят
    # из папки templates/users/logged_out.html
    path('signup/', views.SignUp.as_view(), name='signup'),
    # Полный адрес страницы регистрации - auth/signup/,
    # но префикс auth/ обрабатывется в головном urls.py
    path('login/',
         LoginView.as_view(template_name='users/login.html'), name='login'),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(template_name='users/password_reset_form.html'),
        name='password_reset_form'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(template_name='users/password_change_form.html'),
        name='password_change_form'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
