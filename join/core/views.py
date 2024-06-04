from django.shortcuts import render


def page_not_found(request, exception):
    """Создаёт кастомную страницу 404."""
    # Переменная exception содержит отладочную информацию; 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    context = {
        'path': request.path,
    }
    return render(request, 'core/404.html', context, status=404)

def server_error(request):
    """Создаёт кастомную страницу 500."""
    return render(request, 'core/500.html', status=500)

def permission_denied(request, exception):
    """Создаёт кастомную страницу 403."""
    return render(request, 'core/403.html', status=403)

def csrf_failure(request, reason=''):
    """Страница этой ошибки кастомизируется немного иначе.

    View-функция и шаблон готовится, как и для других страниц,
    но переопределяется не хандлер, а константа CSRF_FAILURE_VIEW в settings.py.
    """
    return render(request, 'core/403csrf.html')
