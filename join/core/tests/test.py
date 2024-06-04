from django.test import TestCase, Client


class TestCastomErrorPages(TestCase):
    """Тестирует кастомные страницы ошибок."""

    def setUp(self):
        # создаём неавторизованный клиент
        self.guest = Client()

    def test_custom_404(self):
        """Test custom 404 page."""
        # посетитель запросил несуществующую страницу
        response = self.guest.get('/simple_page/')
        # проверили код несуществующей страницы, должен быть 404
        self.assertEqual(response.status_code, 404)
        # проверяем, что используется именно созданный нами шаблон
        self.assertTemplateUsed(response, 'core/404.html')


