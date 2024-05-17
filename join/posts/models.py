from django.db import models
# Для работы с моделями импортируется модуль models
from django.contrib.auth import get_user_model
# Для создания поля со ссылкой на модель User импортируется и эта модель:
# она встроена в Django и отвечает за управление пользователями.
from pytils.translit import slugify
from posts.validators import validate_not_empty


User = get_user_model()


class Post(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='Название поста',
        validators=[validate_not_empty],
        help_text='Введите название поста'
        )
    anons = models.CharField(max_length=250, blank=True)
    text = models.TextField(validators=[validate_not_empty])
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
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
        ordering = ['-pub_date']
    


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Читаемая ссылка')
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    # Расширение встроенного метода save(): если поле slug не заполнено -
    # транслитерировать в латиницу содержимое поля title и
    # обрезать до ста знаков
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Обратная связь с администратором сайта.

    Позволяет написать сообщение администратору.
    """
    name = models.CharField(max_length=100, validators=[validate_not_empty])
    email = models.EmailField()
    subject = models.CharField(max_length=100, validators=[validate_not_empty])
    body = models.TextField(max_length=1000)
    is_answered = models.BooleanField(default=False)
