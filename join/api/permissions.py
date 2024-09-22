from rest_framework import permissions


class AuthorPermission(permissions.BasePermission):
    """
    Безопасные запросы GET, OPTIONS и HEAD должны быть разрешены всем,
    даже анонимам. При запросах на изменение или удаление публикации
    проверьте, совпадает ли автор поста obj.author с автором запроса
    (с объектом request.user).
    """

    def has_object_permissions(self, request, view, obj):
        return(
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Безопасные запросы GET, OPTIONS и HEAD должны быть разрешены всем,
    даже анонимам. При запросах на изменение или удаление публикации
    проверьте, совпадает ли автор поста obj.author с автором запроса
    (с объектом request.user). В файле permissions.py опишите класс
    IsAuthorOrReadOnly. Этот класс наследуется от BasePermission из
    пакета rest_framework.permissions. В теле класса переопределите
    метод has_object_permission(), затем подключите класс
    IsAuthorOrReadOnly к необходимому view-классу публикаций.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user == obj.author
        return True
        # альтернативный вариант:
        # return (
        #     request.method in permissions.SAFE_METHODS
        #     or request.user == obj.author
        # )
