from rest_framework.pagination import PageNumberPagination, Response


class CustomPagination(PageNumberPagination):
    """
    Измените используемую по умолчанию структуру ответа при пагинации.
    Уберите поля next и previous из выдачи, а название ключа results
    измените на response.
    """
    # наследуем от PageNumberPagination тк там уже есть
    # нужная структура ответа, которую просто скорректируем
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'response': data,
        })
