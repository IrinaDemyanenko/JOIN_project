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
        self.guest = Client()
    
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
