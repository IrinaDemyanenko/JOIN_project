from django.shortcuts import render
# Импортируем CreateView, чтобы создать ему наследника
from django.views.generic import CreateView
# Функция reverse_lazy позволяет получить URL по параметрам функции path()
# Берём, тоже пригодится
from django.urls import reverse_lazy
# импортируем созданный нами класс формы CreationForm из users/forms.py
from .forms import CreationForm


class SignUp(CreateView):
    # Форма будет работать с созданным нами классом формы CreationForm
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную
    success_url = reverse_lazy('posts:index')
    # posts - пространство имён namespace
    # index - name из path
    template_name = 'users/signup.html'
    # имя шаблона, куда будет передана переменная form с объектом HTML-формы
