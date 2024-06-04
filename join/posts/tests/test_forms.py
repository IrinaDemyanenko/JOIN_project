from django.test import TestCase, Client, override_settings
from django.urls import reverse
from ..models import Post, Group, Comment
from django.contrib.auth import get_user_model
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()
# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostsCreateEditForm(TestCase):
    """Тестирует форму создания и редактирования поста.
    
    Создать пост может только авторизованный пользователь.
    Редактировать пост может только его автор.
    Значит в фикстурах создаём зарегистр. пользователя - автора,
    группу, пост.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных
        cls.user = User.objects.create_user(username='FormUser')
        cls.another_user = User.objects.create(username='AnotherUser')
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

    @classmethod
    def tearDownClass(cls):
        """Удаляет временную папку с медиафайлами TEMP_MEDIA_ROOT после тестов."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        # Модуль shutil - библиотека Python с удобными инструментами 
        # для управления файлами и директориями: 
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое

    def setUp(self):
        # Создаём вэб-клиент для автора поста и логиним его
        # только зарегистр пользователь может создавать посты,
        # только автор поста может его редактировать
        self.author_post = Client()
        self.author_post.force_login(TestPostsCreateEditForm.user)
        # не автор поста, но зарегистрировнный
        self.user_auth = Client()
        self.user_auth.force_login(TestPostsCreateEditForm.another_user)
        # гость сайта
        self.guest = Client()
    

    def test_nonauth_user_cant_comment(self):
        """Оставлять комментарии под постом может только
        зарегистрированный пользователь сайта. Незарегистрированный
        будет перенаправлени на страницу логина.
        """
        # Подсчитаем количество записей в Comment
        comments_count = Comment.objects.count()
        # Данные для формы CommentForm
        form_data = {
            'text': 'тестовый текст для формы комментария',
        }
        # Отправляем POST-запрос с данными формы (по сути создаём комментарий)
        # !!! если получаю статус ответа 200, те редиректа нет, форма не валидна, пост не создан!
        response = self.guest.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': TestPostsCreateEditForm.post.id}
                ),
            data=form_data,
            follow=True  
        )
        # редирект многосоставной, передаём его переменной
        # на страницу логина потом на форму коммента под постом
        redirect = reverse('users:login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': TestPostsCreateEditForm.post.id})
        # страница должна перенаправлять на логин, 
        # ??? почему тогда статус ответа сервера 200, а не 302
        self.assertEqual(response.status_code, 200)
        # число записей не должно увеличится, т к запись не создана из-за переадресации
        self.assertEqual(Comment.objects.count(), comments_count)
        # Проверяем, сработал ли редирект на страницу 'users:login' 
        self.assertRedirects(response, redirect)
        

    def test_auth_user_can_comment(self):
        """Только авторизованный пользователь может оставлять комментарии к постам."""
        # Подсчитаем количество записей в Comment
        comments_count = Comment.objects.count()
        # Информация для заполнения формы комментария
        form_data = {
            'text': 'Тестовый текст комментария)'
        }
        # Создаём коммент - возвращаем путь 'posts:add_comment'
        # заполняем форму, отправляем пост рапрос с информацией
        response = self.user_auth.post(
            reverse('posts:add_comment', kwargs={'post_id': TestPostsCreateEditForm.post.id}),
            form_data,
            follow=True
            )
        # проверяем, что число комментариев в БД увеличилось
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        # Последний комментарий, содержание полей должно совпасть
        # с созданным нами последним комментарием
        comment = Comment.objects.latest('id')
        self.assertEqual(comment.post.id, TestPostsCreateEditForm.post.id)
        self.assertEqual(comment.author, TestPostsCreateEditForm.another_user)
        self.assertEqual(comment.text, form_data['text'])
        # После отправки комментария происходит редирект на страницу post_detail
        # того поста, на странице которого заполняли форму
        self.assertRedirects(
            response,
            reverse(
            'posts:post_detail',
            kwargs={'post_id': TestPostsCreateEditForm.post.id}
            )
        )

    def test_create_post_valid_add_obj_Post_model(self):
        """Тестирует форму создания поста.
        
        При отправке валидной формы со страницы создания поста 
        reverse('posts:post_create') создаётся новая запись в базе данных.
        """
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
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
        # Данные для формы PostForm
        form_data = {
            'text': 'текст',
            'title': 'заголовок',
            'anons': 'анонс',
            'group': self.group.id,
            'image': uploaded
        }
        # Отправляем POST-запрос с данными формы (по сути создаём пост)
        # !!! получаю статус ответа 200, те редиректа нет, форма не валидна, пост не создан!
        response = self.author_post.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True  
        )
        # follow=True, значит, что ответом сервера будет не исходная страница,
        # с которой отправляли форму, а та, на которую будет редирект (т е код
        # проверки состояния страницы будет 200 при успешном тесте, а не 301)
        
        # Проверяем, сработал ли редирект на страницу 'posts:profile' - !!!!!!!!!! 200 а ожидалось 302
        self.assertRedirects(
            response,
            reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
            )
        )
        
        # Проверяем, увеличилось ли число постов !!!!!!!!! 1  != 2
        # Нет, значит пост не был создан, форма была не валидна
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Проверяем, что создалась запись с заданными данными
        # Но этот способ не надёжен, т к проверяет существование такой
        # записи в БД вообще, запись могла существовать и до нашей попытки создания
        # Нужно проверять, вто именно последняя запись с нашими данными
        #self.assertTrue(Post.objects.filter(
                #text='текст',
                #title='заголовок',
                #anons='анонс',
                #group=TestPostsCreateEditForm.group.id,
                #image=uploaded_1  
            #).exists()
        #)

        # Проверяем, что последняя запись с заданными данными
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, TestPostsCreateEditForm.user)
        self.assertEqual(post.group_id, form_data['group'])
        self.assertEqual(post.image.name, 'posts/small.gif')
        # post.image тип ImageFieldFile, а не str. Поэтому вы не можете их сравнить.

    def test_edit_post_valid(self):
        """Тестирует форму редактирования поста.
        
        При отправке валидной формы со страницы редактирования поста 
        reverse('posts:post_edit', args=('post_id',))
        происходит изменение поста со значением post_id в базе данных.
        """
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Данные для формы PostForm
        form_data = {
            'text': 'текст с исправлениями',
            'title': 'заголовок с исправлениями',
            'anons': 'анонс с исправлениями',
            'group': TestPostsCreateEditForm.group.id,
        }
        # Отправляем POST-запрос для получения заполненой формы 
        # поста, который будем редактировать
        response = self.author_post.post(
            reverse('posts:post_edit', 
                    kwargs={'post_id': TestPostsCreateEditForm.post.id}),
            data=form_data,
            follow=True  
        )
        # follow=True, значит, что ответом сервера будет не исходная страница,
        # с которой отправляли форму, а та, на которую будет редирект (т е код
        # проверки состояния страницы будет 200 при успешном тесте, а не 302)
        
        # Проверяем, сработал ли редирект на страницу 'posts:post_detail'
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': TestPostsCreateEditForm.post.id}))
        
        # Проверяем, НЕ увеличилось ли число постов
        # при редактировании пост не создаётся, а меняется 
        self.assertEqual(Post.objects.count(), posts_count)

        # передаём отредактированный пост в переменную (надёжная проверка)
        edited_post = Post.objects.get(id=TestPostsCreateEditForm.post.id)

        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.title, form_data['title'])
        self.assertEqual(edited_post.anons, form_data['anons'])
        self.assertEqual(edited_post.group_id, form_data['group'])

