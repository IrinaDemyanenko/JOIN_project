from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Post, Group  # подняться на два уровня выше
# чтобы протестировать страницы создания и редактирования поста
# нужно создать пост и трёх клиентов (зарегистр автора поста;
# не автора, но зарегистрированного; и посетителя сайта)
# а так же сам пост и группу.
# Для каждого создать словарь адресов и кодов ответа сервера.

User = get_user_model()


class TestPostsURL(TestCase):
    """Тестирует URL приложения posts."""

    # готовим данные для теста класс-методом
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # чтобы не было ошибки атрибута
        cls.user = User.objects.create_user(username='my_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_to_test_only',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            title='Тестовый постик',
            anons='Очень сложный тест!',
            text=('Я помню чудное мгновенье, передо мной явилась ты! '
                  'Как мимолётное виденье, как гений чистой красоты!'),
            group=cls.group,
            author=cls.user
        )
        cls.another_user = User.objects.create_user('another_user')

    def setUp(self):
        # просто посетитель сайта
        self.visitor = Client()
        # автор поста - тоже создаём для него вэб-клиента
        self.author_post = Client()
        # регистрируем автора поста на сайте
        self.author_post.force_login(TestPostsURL.user)
        # для второго зарегистрир пользователя, не автора поста
        # тоже создаём вэб-клиента
        self.auth_user = Client()
        # регистр. 2-ого пользователя на сайте
        self.auth_user.force_login(TestPostsURL.another_user)

    #def test_home_url_exists_at_desired_location(self):
        #"""Страница / доступна любому пользователю."""
        #response = self.visitor.get('/')
        #self.assertEqual(response.status_code, 200)

    #def test_group_slug_to_test_only_url_exists_at_desired_location(self):
        #"""Страница '/group/slug_to_test_only/' доступна любому пользователю."""
        #response = self.visitor.get('/group/slug_to_test_only/')
        #self.assertEqual(response.status_code, 200)

    def test_visitor_response_status_code(self):
        """Тестирует ответ сервера для гостя сайта."""
        address_list_visitor = {
            '/': 200,
            '/group/slug_to_test_only/': 200,
            '/profile/my_name/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,  # редирект на логин на сайте
            '/create/': 302,  # редирект на логин на сайте
            '/uexisting_page/': 404
        }
        for address, code in address_list_visitor.items():
            with self.subTest(address=address):
                response = self.visitor.get(address)
                self.assertEqual(response.status_code, code,
                                 f'Гость сайта для адреса {address} получил неверный код ответа!')

    def test_redirect_visitor_on_login(self):
        """Тестирует редиректы для гостя сайта."""
        address_redirect_visitor = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for address, redir in address_redirect_visitor.items():
            with self.subTest(address=address):
                response = self.visitor.get(address, follow=True)
                self.assertRedirects(response, redir)

    def test_author_post_response_status_code(self):
        """Тестирует ответ сервера для зарегистрировнного автора поста."""
        address_list_author_post = {
            '/': 200,
            '/group/slug_to_test_only/': 200,
            '/profile/my_name/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 200,  # редирект на логин на сайте
            '/create/': 200,  # редирект на логин на сайте
            '/uexisting_page/': 404
        }
        for address, code in address_list_author_post.items():
            with self.subTest(address=address):
            # Для каждого экземпляра вложенный тест
                response = self.author_post.get(address)
                self.assertEqual(response.status_code, code,
                             f'Автор поста для адреса {address} получил неверный код ответа!')

    def test_auth_user_response_status_code(self):
        """Тестирует код ответа сервера для зарегистрированного
        пользователя, не автора поста.
        """
        address_list_auth_user = {
            '/': 200,
            '/group/slug_to_test_only/': 200,
            '/profile/my_name/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,  # редирект на логин на сайте
            '/create/': 200,  # редирект на логин на сайте
            '/uexisting_page/': 404
        }
        for address, code in address_list_auth_user.items():
            with self.subTest(address=address):
                response = self.auth_user.get(address)
                self.assertEqual(response.status_code, code,
                                 f'Зарегистрированный пользователь для адреса '
                                 f'{address} получил неверный код ответа!')

    def test_redirect_auth_user(self):
        """Тестирует редирект для зарегистрированного пользователя,
        но не автора поста со страницы '/posts/1/edit/' на
        '/auth/login/?next=/posts/1/edit/'.
        """
        response = self.auth_user.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')
        # не автору поста редактировать нельзя, но можно читать
        # перенаправляет на страницу чтения поста

    def test_adress_uses_correct_template(self):
        """Для страницы вызывается ожидаемый HTML-шаблон."""
        address_template = {
            '/': 'posts/index.html',
            '/group/slug_to_test_only/': 'posts/group_posts.html',
            '/profile/my_name/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
        }
        for address, templ in address_template.items():
            with self.subTest(address=address):
                response = self.author_post.get(address)
                # автор поста - т к у него максимальные права (кроме админа)
                self.assertTemplateUsed(response, templ)