from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Post, Group


User = get_user_model()


class TestPostsViews(TestCase):
    """Тестирует views приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # готовим данные для тестирования
        # создадим зарегистр автора поста, 
        # просто зарегистр пользователя, не автора
        # группу и пост в этой группе
        cls.user = User.objects.create_user(username='My_user_author')
        cls.another_user = User.objects.create_user(username='Another_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_to_test',
            description='Здесь описание моей интереснейшей группы для теста!'
        )
        cls.post = Post.objects.create(
            title='Тестовый постик!',
            anons='Анонс для затравочки)',
            text='Здест текст для тестового поста!',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        # cоздаёт 3 вэб-клиента: для гостя сайта,
        # зарегистр пользователя и автора поста
        self.visitor = Client()
        self.author_post = Client()
        self.author_post.force_login(TestPostsViews.user)
        self.another_user = Client()
        self.another_user.force_login(TestPostsViews.another_user)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        # клиент гостя, т к минимальные права на сайте
        response = self.visitor.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым.
        # Из ответа сервера берём словарь контекст, значение ключа page_object;
        # т к это список постов, берём первый элемент по индексу 0
        first_post = response.context['page_object'][0]
        post_title_0 = first_post.title
        post_anons_0 = first_post.anons
        post_text_0 = first_post.text
        post_author_0 = first_post.author
        post_group_0 = first_post.group
        self.assertEqual(post_title_0, 'Тестовый постик!')
        self.assertEqual(post_anons_0, 'Анонс для затравочки)')
        self.assertEqual(post_text_0, 'Здест текст для тестового поста!')
        self.assertEqual(post_author_0, 'My_user_author')
        self.assertEqual(post_group_0, 'Тестовая группа')


from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Post, Group
from django import forms


User = get_user_model()


class TestPostsViews(TestCase):
    """Тестирует views приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # готовим данные для тестирования
        # создадим зарегистр автора поста, 
        # просто зарегистр пользователя, не автора
        # группу и пост в этой группе
        cls.user = User.objects.create_user(username='My_user_author')
        cls.another_user = User.objects.create_user(username='Another_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_to_test',
            description='Здесь описание моей интереснейшей группы для теста!'
        )
        cls.post = Post.objects.create(
            title='Тестовый постик!',
            anons='Анонс для затравочки)',
            text='Здест текст для тестового поста!',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        # cоздаёт 3 вэб-клиента: для гостя сайта,
        # зарегистр пользователя и автора поста
        self.visitor = Client()
        self.author_post = Client()
        self.author_post.force_login(TestPostsViews.user)
        self.another_user = Client()
        self.another_user.force_login(TestPostsViews.another_user)

    # проверка namespace:name
    # Напишите тесты, проверяющие, что во view-функциях
    # используются правильные html-шаблоны.
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        
        При обращении к определённому имени (указанному в path()
        в аргументе name) для отображения страниц вызывается ожидаемый
        HTML-шаблон.
        Обратиться из кода к адресам приложения по имени name можно
        через метод reverse():
        self.client.get(reverse('имя_приложения:name')).
        Чтобы проверить, какой шаблон использует view-класс или view-функция,
        в django.test есть утверждение assertTemplateUsed.
        """
        # Собираем в словарь пары "имя_html_шаблона: reverse(‘namespace:name’)
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'slug_to_test'}): (
                'posts/group_posts.html'),
            reverse('posts:profile', kwargs={'username': 'My_user_author'}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/post_create.html')
        }
        # Проверяем, что при обращении к name вызывается соответствующий
        # HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.author_post.get(reverse_name)
                self.assertTemplateUsed(response, template)
        # !!! почему-то ошибки выдаёт последовательно, а не все сразу
        # во всех вложенных тестах

    def check_post_info(self, post):
        """Проверяет правильность заполнения полей поста."""
        with self.subTest(post=post):
            self.assertEqual(post.title, self.post.title)
            self.assertEqual(post.anons, self.post.anons)
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)


        # Проверка словарей контекста
        # должны передавать в шаблон ожидаемую информацию

        # Проверяем, что словарь context страницы /
        # в первом элементе списка page_object содержит ожидаемые значения
    
    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        # клиент гостя, т к минимальные права на сайте
        response = self.visitor.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым.
        # Из ответа сервера берём словарь контекст, значение ключа page_obj;
        # т к это список постов, берём первый элемент по индексу 0
        first_post = response.context['page_obj'][0]
        self.check_post_info(first_post)

    def test_group_posts_shows_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом.
        
        Ожидаем - список постов, отфильтрованных по группе.
        Проверяем, что первый (он же единственный) пост соответствует
        ожидаемой структуре.
        """
        response = self.visitor.get(reverse(
            'posts:group_list', kwargs={'slug': 'slug_to_test'}))
        first_group_post = response.context['page_obj'][0]
        self.check_post_info(first_group_post)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом.
        
        Ожидаем - список постов, отфильтрованных по автору.
        Проверяем, что первый (он же единственный) пост соответствует
        ожидаемой структуре.
        """
        response = self.author_post.get(reverse(
            'posts:profile', kwargs={'username': 'My_user_author'}))
        first_author_post = response.context['page_obj'][0]
        self.check_post_info(first_author_post)

    def test_post_detail_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом.
        
        Ожидаем - постов.
        Проверяем, что первый (он же единственный) пост соответствует
        ожидаемой структуре.
        """
        response = self.author_post.get(reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        post_detail = response.context['post']
        self.check_post_info(post_detail)

    def test_post_create_shows_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом.
        
        На страницу передаётся форма создания поста.
        Создаём словарь ожидаемых типов полей формы,
        указываем, объектами какого класса должны быть поля формы.
        """
        response = self.author_post.get(reverse('posts:post_create'))
        form_create_post = {
            'text': forms.fields.CharField,
            'title': forms.fields.CharField,
            'anons': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_create_post.items():
            with self.subTest(value=value):
                ## Передаём переменной одно из полей формы
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
