from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Group
from django.contrib.auth import get_user_model


User = get_user_model()


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
        # Создаём вэб-клиент для автора поста и логиним его
        # только зарегистр пользователь может создавать посты,
        # только автор поста может его редактировать
        self.author_post = Client()
        self.author_post.force_login(TestPostsCreateEditForm.user)

    def test_create_post_valid_add_obj_Post_model(self):
        """Тестирует форму создания поста.
        
        При отправке валидной формы со страницы создания поста 
        reverse('posts:post_create') создаётся новая запись в базе данных.
        """
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Данные для формы PostForm
        form_data = {
            'text': 'текст',
            'title': 'заголовок',
            'anons': 'анонс',
            'group': TestPostsCreateEditForm.group.id
        }
        # Отправляем POST-запрос
        response = self.author_post.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True  
        )
        # follow=True, значит, что ответом сервера будет не исходная страница,
        # с которой отправляли форму, а та, на которую будет редирект (т е код
        # проверки состояния страницы будет 200 при успешном тесте, а не 301)
        
        # Проверяем, сработал ли редирект на страницу 'posts:profile' - !!!!!!!!!! 200 а ожидалось 302
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        
        # Проверяем, увеличилось ли число постов !!!!!!!!! 1  != 2
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Проверяем, что создалась запись с заданными данными
        self.assertTrue(Post.objects.filter(
                text='текст',
                title='заголовок',
                anons='анонс',
                group=TestPostsCreateEditForm.group.id  
            ).exists()
        )

        # Проверяем, что последняя запись с заданными данными
        post = Post.objects.latest('id')
        self.assertTrue(post.text == form_data['text'])
        self.assertTrue(post.author == TestPostsCreateEditForm.user)
        self.assertTrue(post.group_id == form_data['group'])

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
            'group': TestPostsCreateEditForm.group.id
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


        # Проверяем, что создалась запись с заданными данными (не очень проверка)
        self.assertTrue(Post.objects.filter(
                text='текст с исправлениями',
                title='заголовок с исправлениями',
                anons='анонс с исправлениями',
                group=TestPostsCreateEditForm.group.id  
            ).exists()
        )


