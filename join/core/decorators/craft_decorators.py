from functools import wraps
from django.shortcuts import redirect
import time


def authorized_only(func):
    """Декоратор проверки авторизации пользователя.

    Статусы: авторизован, не автризован.
    Пользователям будут доступны разные возможности,
    у авторизованных будет больше возможностей, другие ссылки.
    """
    @wraps(func)  # Задекорировали обёртку
    # Функция-обёртка в декораторе может быть названа как угодно
    def check_user(request, *args, **kwargs):
        # В любую view-функции первым аргументом передаётся объект request,
        # в котором есть булева переменная is_authenticated,
        # определяющая, авторизован ли пользователь.
        if request.user.is_authenticated:
            # Возвращает view-функцию, если пользователь авторизован.
            return func(request, *args, **kwargs)
        # Если пользователь не авторизован — отправим его на страницу логина.
        return redirect('/auth/login/')
    return check_user


def time_check(func):
    """Декоратор для замера времени выполнения функции."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)  # результат работы ф-ии сохраним в переменной
        execution_time = round((time.time() - start_time()), 1)
        print(f'Время выполнения программы: {execution_time} с.')
        return result
    return wrapper
