from django.db import models
# Для работы с моделями импортируется модуль models
from django.contrib.auth import get_user_model
# Для создания поля со ссылкой на модель User импортируется и эта модель:
# она встроена в Django и отвечает за управление пользователями.
from pytils.translit import slugify
from posts.validators import validate_not_empty


User = get_user_model()


class Tag(models.Model):
    """Хэштэги к постам.
    
    Связаны с постами отношением «многие-ко-многим».
    При запросе постов должна возвращаться информация о всех
    связанных с конкретным постом хештегах, а при добавлении
    или обновлении поста нужно обеспечить возможность
    передавать названия хештегов списком прямо в теле запроса.
    Без указания хештегов пост через API тоже должен создаваться.
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


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


class Post(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='Название поста',
        validators=[validate_not_empty],
        help_text='Введите название поста'
        )
    anons = models.CharField(max_length=250, blank=True)
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
        validators=[validate_not_empty],
        )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        )
    group = models.ForeignKey(
        Group,
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
        related_name='posts',
        verbose_name='Автор'
        )
    # в объекте пользователя появилось поле posts,
    # в котором хранятся ссылки на все посты этого автора.
    # И теперь можно получить список постов автора,
    # обратившись к его свойству posts
    # Поле для картинки (необязательное) 
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    # Аргумент upload_to указывает директорию, 
    # в которую будут загружаться пользовательские файлы. 
    # Путь в параметре upload_to указывается относительно адреса,
    # указанного в settings.py в MEDIA_ROOT: в нём устанавливают полный путь
    # к директории, куда будут загружаться файлы пользователей: обычно её
    # называют media/.
    # таким образом картинки, прикреплённые к постам, будут сохраняться
    # в директории media/posts.

    # Связь будет описана через вспомогательную модель TagPost
    # Связываем модель Post с моделью Tag через таблицу связи TagPost
    tag = models.ManyToManyField(Tag, through='TagPost')
    
    def __str__(self) -> str:
        return self.text[:30]

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']
    

# В этой модели будут связаны id поста и id его тэгов
# вспомогательная таблица для связи "многие-ко-многим"
class TagPost(models.Model):
    """Связывает посты и тэги.
    
    Каждый тэг может принадлежать многим постам, так же
    как и каждый пост может обладать многими тэгами.
    Связь "многие-ко-многим".
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post} {self.tag}'


class Comment(models.Model):
    """Создание комментария к посту.
    
    Комментировать может только зарегистрированный пользователь.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Напишите комментарий к посту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Имя автора комментария'
    )
    text = models.TextField(
        max_length=500,
        verbose_name='Комментарий',
        validators=[validate_not_empty]
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата'
    )

    def __str__(self):
        return self.text[:30]
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created']


class Follow(models.Model):
    """Система подписки на авторов."""
    # пользователь, который подписывается
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Пользователь, который подписывается на автора'
    )
    # пользователь, на которого подписываются
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор, на которого подписываются'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Contact(models.Model):
    """Обратная связь с администратором сайта.

    Позволяет написать сообщение администратору.
    """
    name = models.CharField(max_length=100, validators=[validate_not_empty])
    email = models.EmailField()
    subject = models.CharField(max_length=100, validators=[validate_not_empty])
    body = models.TextField(max_length=1000)
    is_answered = models.BooleanField(default=False)
