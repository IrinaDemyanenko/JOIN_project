from django.db import models
# Для работы с моделями импортируется модуль models
from django.contrib.auth import get_user_model
# Для создания поля со ссылкой на модель User импортируется и эта модель:
# она встроена в Django и отвечает за управление пользователями.
from django.utils.text import slugify

User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=50, default='Название')
    anons = models.CharField(max_length=250)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts'
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
        )  
    # в объекте пользователя появилось поле posts,         
    # в котором хранятся ссылки на все посты этого автора. 
    # И теперь можно получить список постов автора, 
    # обратившись к его свойству posts
  
    def __str__(self) -> str:
        return self.title
  
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Читаемая ссылка')
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
