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
        Значения полей постов и групп лучше передавать не прямо:
        'Тестовый постик!' лучше как self.post.title. 
        """
        # Собираем в словарь пары "имя_html_шаблона: reverse(‘namespace:name’)
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): (
                'posts/group_posts.html'),
            reverse('posts:profile', kwargs={'username': self.user.username}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): (
                'posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): (
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
            'posts:group_list', kwargs={'slug': self.group.slug}))
        first_group_post = response.context['page_obj'][0]
        self.check_post_info(first_group_post)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом.
        
        Ожидаем - список постов, отфильтрованных по автору.
        Проверяем, что первый (он же единственный) пост соответствует
        ожидаемой структуре.
        """
        response = self.author_post.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_author_post = response.context['page_obj'][0]
        self.check_post_info(first_author_post)

    def test_post_detail_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом.
        
        Ожидаем - постов.
        Проверяем, что первый (он же единственный) пост соответствует
        ожидаемой структуре.
        """
        response = self.author_post.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
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
            'group': forms.fields.ChoiceField,  # тк группа созд. админом
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_create_post.items():
            with self.subTest(value=value):
                ## Передаём переменной одно из полей формы
                form_field = response.context.get('form').fields.get(value)
                # Из ответа сервера берём словарь контекст, из словаря берём форму,
                # из формы берём поля, из полей значения.
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_edit_shows_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом.
        
        На страницу передаётся форма редактирования поста, отфильтрованного
        по id.
        Создаём словарь ожидаемых типов полей формы,
        указываем, объектами какого класса должны быть поля формы.
        """
        response = self.author_post.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_edit_post = {
            'text': forms.fields.CharField,
            'title': forms.fields.CharField,
            'anons': forms.fields.CharField,
            'group': forms.fields.ChoiceField,  # тк группа созд. админом
        }
        for value, expected in form_edit_post.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class TestPaginator(TestCase):
    """Тестирует паджинатор на страницах.
    
    Паджинатор доступен всем пользователям, но проверить нужно профайл,
    значит создаём зарегистрированного пользователя.
    Паджинатор появляется в случае, если объетов на странице больше 10,
    значит создаём 15 тестовых объектов (постов).
    Проверяем 3 страницы: index, group/slug, profile/username.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author_post')
        cls.group = Group.objects.create(
            title='Тестирует паджинатор!',
            slug='my_paginator_test',
            description='Описание группы'
        )

        # создадим 15 постов в БД, принадлежащих одному автору
        # и одной группе
        for i in range(15):  # from 0 to 14
            Post.objects.create(
                title=f'Тестовый постик {i}!',
                anons=f'Анонс {i} для затравочки)',
                text=f'Здест текст {i} для тестового поста!',
                group=cls.group,
                author=cls.user,
            )
            i += 1

    def setUp(self):
        # создадим вэб-клиент для зарег. автора постов
        self.user_auth = Client()
        # зарегистрируем автора постов
        self.user_auth.force_login(TestPaginator.user)

    def test_paginator(self):
        """Тестирует паджинатор на страницах."""
        # список страниц
        reverse_names_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]
        for reverse_name in reverse_names_pages:
            with self.subTest(reverse_name=reverse_name):
                response1 = self.user_auth.get(reverse_name)
                response2 = self.user_auth.get(reverse_name + '?page=2')
                # тест на кол-во объектов на первой странице = 10
                self.assertEqual(len(response1.context['page_obj']), 10)
                # тест на кол-во объектов на второй странице = 5
                self.assertEqual(len(response2.context['page_obj']), 5)



