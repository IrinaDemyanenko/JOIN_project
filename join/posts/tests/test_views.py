from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Post, Group, Follow
from django import forms
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache




User = get_user_model()
# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        # Для тестирования загрузки изображений 
        # берём байт-последовательность картинки, 
        # состоящей из двух пикселей: белого и чёрного
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            title='Тестовый постик!',
            anons='Анонс для затравочки)',
            text='Здест текст для тестового поста!',
            group=cls.group,
            author=cls.user,
            image=uploaded
        )

    
    @classmethod
    def tearDownClass(cls):  # отрабатывает после тестов
        """Удаляет папку TEMP_MEDIA_ROOT с тестовыми медиафайлами."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        # Модуль shutil - библиотека Python с удобными инструментами 
        # для управления файлами и директориями: 
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое

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
        cache.clear()
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
        """Проверяет правильность заполнения полей поста.
        
        Вспомогательная функция.
        Будем применять вдальнейшем, в тестах.
        """
        with self.subTest(post=post):
            self.assertEqual(post.title, self.post.title)
            self.assertEqual(post.anons, self.post.anons)
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)
            self.assertEqual(post.image, self.post.image)


        # Проверка словарей контекста
        # должны передавать в шаблон ожидаемую информацию

        # Проверяем, что словарь context страницы /
        # в первом элементе списка page_object содержит ожидаемые значения
    
    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        # клиент гостя, т к минимальные права на сайте
        cache.clear()
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
            'group': forms.fields.ChoiceField,  # тк группа созд. админом, можно только выбрать
            'image': forms.fields.ImageField
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
            'group': forms.fields.ChoiceField,  # тк группа созд. админом, можно только выбрать
            'image': forms.fields.ImageField
        }
        for value, expected in form_edit_post.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Проверяет работу кэша на главной странице.
        
        Кэширование подключено к шаблону posts/index.html,
        ключ index_page, под которым данные хранятся в кэше.
        """
        # на главной странице все посты, значит сейчас все они в кэше
        # зарегистрированный пользователь заходит на главную стр
        # добавим новый пост, он должен будет появиться на главной странице
        # только через 20 секунд
        cache.clear()
        response = self.another_user.get(reverse('posts:index'))
        posts_cache = response.content
        new_post = Post.objects.create(
            title='Новый пост',
            anons='Новый анонс',
            text='Здест текст',
            group=TestPostsViews.group,
            author=TestPostsViews.user,
        )
        # зарегистрированный пользователь заходит на главную стр после
        # создания поста, кэша ещё нет, он сейчас будет записываться с постом
        #new_post.delete()
        # зарегистрированный пользователь заходит на главную стр после удаления поста
        second_response = self.another_user.get(reverse('posts:index'))
        second_posts = second_response.content
        # но т к 20 секунд не прошло, контекст страницы должен совпасть 
        self.assertEqual(posts_cache, second_posts)
        # теперь очистим кэш и перезайдем на главную страницу
        cache.clear()
        new_response = self.another_user.get(reverse('posts:index'))
        # кэш перезаписался, теперь там ещё один пост,
        # результат первоначального кэша и нового не должен совпадать
        self.assertNotEqual(posts_cache, new_response.content)



@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        # Для тестирования загрузки изображений 
        # берём байт-последовательность картинки, 
        # состоящей из двух пикселей: белого и чёрного
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
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
                image=uploaded
            )
            i += 1
    
    @classmethod
    def tearDownClass(cls):  # отрабатывает после тестов
        """Удаляет папку TEMP_MEDIA_ROOT с тестовыми медиафайлами."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        # Модуль shutil - библиотека Python с удобными инструментами 
        # для управления файлами и директориями: 
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое

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


class TestFollow(TestCase):
    """Тестирует сервис подписки/отписки на автора."""
    # arrange - готовим тестовые данные
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создадим двух зарегистр пользователей, один будет подписан на другого
        cls.user = User.objects.create_user(username='First_author')
        cls.another_user = User.objects.create_user(username='Second_user')
        cls.third_user = User.objects.create_user(username='Third_user')
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
        # cоздаёт 4 вэб-клиента: для гостя сайта,
        # зарегистр пользователей и автора поста
        self.author = Client()
        self.author.force_login(TestFollow.user)
        self.auth_user = Client()
        self.auth_user.force_login(TestFollow.another_user)
        self.one_more = Client()
        self.one_more.force_login(TestFollow.third_user)
        
    
    def test_auth_user_can_follow_unfollow(self):
        """Тест: Зарегистрированный пользователь может подписываться
        на других зарегистрированных пользователей и отписываться от них.
        """
        # посчитаем кол-во записей в моделе Follow
        follow_count = Follow.objects.count()
        # не автор, но зарег польз, заходит в профиль автора и подписывается на него
        # в теле view прописано создание записи в моделе Follow
        response = self.auth_user.get(reverse(
            'posts:profile_follow', kwargs={'username': TestFollow.user.username}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        response_unfollow = self.auth_user.get(reverse(
            'posts:profile_unfollow', kwargs={'username': TestFollow.user.username}))
        self.assertEqual(Follow.objects.count(), follow_count)
        

    def test_follower_post_feed(self):
        """Тест: Новая запись автора появляется у тех, кто на него подписан."""
        # подпишем одного авторизованного пользователя на другого через модель
        Follow.objects.create(
            user=TestFollow.another_user,
            author=TestFollow.user
        )
        # пока один пост (из setUpClass)
        response = self.auth_user.get(reverse('posts:follow_index'))
        # создадим новый пост
        post = Post.objects.create(
            title='Новый пост',
            text='Здесь текст',
            author=TestFollow.user
        )
        response_2 = self.auth_user.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']) + 1,
            len(response_2.context['page_obj'])
        )
        self.assertIn(post, response_2.context['page_obj'].object_list)
        

    def test_nonfollower_post_feed(self):
        """Тест: Новая запись автора не появляется у тех, кто не подписан."""
        # подпишем одного авторизованного пользователя на другого через модель
        Follow.objects.create(
            user=TestFollow.another_user,
            author=TestFollow.user
        )
        # создадим новый пост
        post = Post.objects.create(
            title='Новый пост',
            text='Здесь текст',
            author=TestFollow.user
        )
        response = self.one_more.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
