from django.test import TestCase, Client

class StaticURLTests(TestCase):
    """Тестирует статические страницы проекта."""

    @classmethod
    def setUpTestData(cls):
        """Готовит данные для теста.

        Вызывается один раз перед запуском всех test case.
        """
        # Создаём экземпляр клиента. Он неавторизован.
        cls.guest_client = Client()
        # cls.auth_client = Client()  # не знаю, как задать авторизованного клиента

    def test_homepage(self):
        """Тестирует главную страницу."""

        # Отправляем запрос через client,
        # созданный в setUpTestData()
        response = StaticURLTests.guest_client.get('/')
        self.assertEqual(response.status_code, 200,
                         'Главная страница недоступна!')

    def test_author_page(self):
        """Тестирует страницу об авторе."""
        response = StaticURLTests.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200,
                         'Страница "об авторе" недоступна!')

    def test_tech_page(self):
        """Тестирует страницу технологии."""
        response = StaticURLTests.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200,
                         'Страница технологии недоступна!')