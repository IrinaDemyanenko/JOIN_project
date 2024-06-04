from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Post, Group, Comment  # подняться на два уровня выше

User = get_user_model()


class TestPostModel(TestCase):
    """Тестирует модель Post."""

    # готовим данные для теста класс-методом
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # чтобы не было ошибки атрибута
        cls.user = User.objects.create_user(username='my_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
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

    def test_model_have_correct_str_method(self):
        """Метод __str__ выдаёт title."""
        # объект созданный класс-методом post, из него берём title
        # переводим объект в строку, чтобы проверить работу метода
        act = str(TestPostModel.post)
        # ожидаемый результат
        result = TestPostModel.post.text[:30]
        self.assertEqual(act, result,
                         'Метод __str__ модели Post работает неверно!')

    def test_verbose_name_correct(self):
        """Проверяет правильность verbose_name в полях модели Post."""
        post = TestPostModel.post  # создали объект
        fields_verbose_names = {
            'title': 'Название поста',
            'group': 'Группа'
        }
        for field, expected_value in fields_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value,
                    f'Verbose_name для поля {field} неверно!'
                    )

    def test_help_text_corect(self):
        """Проверяет правильность help_text в полях модели Post."""
        post = TestPostModel.post
        fields_help_texts = {
            'title': 'Введите название поста',
            'group': 'Выберите группу'
        }
        for field, expected_value in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value,
                    f'Help_text для поля {field} неверно!'
                )


class TestGroupModel(TestCase):
    """Тестирует работу модели Group."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Ж'*100,
            description='Тестовое описание тестовой группы'
        )

    def test_class_method_str_correct(self):
        """Метод __str__ выдаёт title."""
        # TestGroupModel.group - это объект, созданный методом класса
        act = str(TestGroupModel.group)  # отработал метод для объекта
        result = TestGroupModel.group.title  # ожидаем увидеть title
        self.assertEqual(act, result,
                         'Метод __str__ модели Group работает неверно!')

    def test_title_convert_to_slug(self):
        """Тестирует преобразование заголовка в slug."""
        # в самом объекте я не задала слаг, хочу проверить корректность
        # преобразования
        slug = TestGroupModel.group.slug
        result = 'zh'*50
        self.assertEqual(slug, result,
                         'Метод slug модели Group работает неверно!')


class TestCommentModel(TestCase):
    """Тестирует модель Comment.
    
    Комментарий может написать только авторизованный пользователь
    к конкретному посту.
    """
    # готовим данные для теста
    # создаём пост и авторизованный клиент
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Auth_uset_test')
        cls.another_user = User.objects.create_user(username='Comment_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='slug_group_test',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            title='Тестовый заголовок поста',
            text='Текст для поста',
            group=cls.group,
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.another_user,
            text='Волшебный пост! Спасибо автор!'
        )

    def test_class_method_str_correct(self):
        """Тестирует метод __str__."""
        act = str(TestCommentModel.comment)
        result = TestCommentModel.comment.text[:30]
        self.assertEqual(act, result)
    
    def test_verbose_name_correct(self):
        """Тестирует verbose_name полей модели Comment."""
        comment = TestCommentModel.comment
        fields_verbose_names = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Комментарий',
            'created': 'Дата'
        }
        for field, expected in fields_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected,
                    f'Verbose_name для поля {field} некорректно!'
                )
