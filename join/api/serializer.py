
from posts.models import Comment, Follow, Post, Group, Tag, TagPost, User
from rest_framework import serializers

from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag Model.

    Converts model`s objects to JSON and back."""

    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post Model.

    Converts model`s objects to JSON and back.
    """
    # group = serializers.StringRelatedField(read_only=True)
    # это поле можно переопределить, чтобы в ответе видеть не id а имя
    # many=True не пишем тк у поста может быть только одна группа
    # Переопределяем поле group
    # required=False значит, что поле необязательное
    # Для работы в режиме записи необходимо дополнительно передать
    # аргумент queryset
    # slug_field='slug' передаём поле slug из модели Group
    group = serializers.SlugRelatedField(
        queryset=Group.objects.all(),
        required=False,
        slug_field='slug'
    )
    # переопределим поле tag
    # назначим типом поля сериализатор TagSerializer,
    # который передаст в это поле список объектов
    tag = TagSerializer(many=True, required=False)

    # поле, где будет инф о кол-ве символов в статье
    character_quantity = serializers.SerializerMethodField()

    # переименуем поле pub_date
    publication_date = serializers.DateTimeField(
        source='pub_date', read_only=True
        )

    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Post  # работает с моделью Post
        fields = [
            'title', 'anons', 'text', 'publication_date',
            'group', 'author', 'tag', 'character_quantity'
            ]
        # Указываем поля модели, с которыми будет работать сериализатор;
        # поля модели, не указанные в перечне, сериализатор будет игнорировать.
        # укажите поля, доступные только для чтения
        read_only_fields = ['author', ]

    # для записи новых данных во вложенный сериализатор (POST запрос)
    # переопределим метод create, укажем явным образом, какие
    # записи в каких таблицах нужно создать
    def create(self, validated_data):
        # Если в исходном запросе не было поля tag
        # доступ к тем данным, которые были переданы в сериализатор
        # хранятся в словаре serializer.initial_data
        if 'tag' not in self.initial_data:
            # То создаём запись о посте без тэгов используя
            # словарь с данными прошедшими валидацию
            post = Post.objects.create(**validated_data)
            return post

        # Если в исходном запросе было поле tag
        # Из списка serializer.validated_data извлечь и сохранить
        # в переменную элемент tags список тэгов
        # Уберем список достижений из словаря validated_data
        # и сохраним его
        tags = validated_data.pop('tag')

        # создадим новый пост пока без тэгов, данных достаточно
        # тэги пока лежат в сторонке, ждут обработки
        post = Post.objects.create(**validated_data)

        # если проверяемый элемент уже есть в базе — в таблицу
        # связей TagPost добавить связь этого тэга с новым постом;
        # если проверяемого элемента в базе нет — в базе достижений
        # создать новую запись и в таблицу связей TagPost добавить
        # связь этого тэга с новым постом

        # Для каждого тэга из списка тэгов
        for tag in tags:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_tag, status = Post.objects.get_or_create(
                **tag)
            # Поместим ссылку на каждый тэг во вспомогательную таблицу
            # Не забыв указать к какому посту он относится
            TagPost.objects.create(tag=current_tag, post=post)
        # вернуть JSON с объектом свежесозданного поста и списком его тэгов
        return post

    # метод для подсчёта символов в статье
    def get_character_quantity(self, obj):
        """This method counts character quantity at a particular post."""
        return len(obj.text)

    # def update(self, instance, validated_data):
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.anons = validated_data.get('anons', instance.anons)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.group = validated_data.get('group', instance.group)
    #     instance.author = validated_data.get('author', instance.author)
    #     instance.tag = validated_data.get('tag', instance.tag)
    #     instance.save()
    #     return instance

class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Group.

    Группы может создавать только админ сайта, значит доступны только GET запросы.
    """

    class Meta:
        model = Group
        fields = [
            'title', 'slug', 'description',
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            'post', 'author', 'text', 'created',
        ]
        read_only_fields = ['post', ]


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""


    # Для определения пользователя есть встроенный класс CurrentUserDefault
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
        )
    author = serializers.SlugRelatedField(
        slug_field='username',
        # Набор запросов, используемый для поиска экземпляра модели при проверке
        # ввода поля. Отношения должны либо явно задать queryset, либо установить
        # read_only=True, но это поле обязательное т к оно испольукется в валидаторе
        # и назначить его по умолчанию тоже нельзя, значит зададим параметр queryset
        queryset=User.objects.all(),
        )

    class Meta:
        model = Follow
        fields = [
            'user', 'author'
        ]
        # чтобы не допустить подписку на одного и того же автора дважды
        # Такую же проверку нужно реализовать и на уровне сериализатора.
        # UniqueTogetherValidator всегда накладывает неявное ограничение на то,
        # что все поля, к которым он применяется, всегда рассматриваются
        # как обязательные. Поля со значениями по умолчанию являются исключением
        # из этого правила, так как они всегда предоставляют значение, даже
        # если оно опущено при вводе пользователем.
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
                message=('You have been already following this author!')
            )
        ]
    # Чтобы выполнить проверку, требующую доступа к нескольким полям,
    # добавьте в сериализатор метод validate(). Этот метод принимает
    # один аргумент — словарь со значениями полей.
    # !!!НЕ РАБОТАЕТ!!!
    # def validate(self, data):
    #     data = self.data.is_valid()
    #     # если значение поля user совпадает со значением поля author
    #     if data['user'] == data['author']:
    #         # вызвать ошибку валидации и отправить сообщение
    #         raise ValidationError('You can`t follow yourself!')
    #     # если все хорошо - передать словать с данными для внесения записи в БД
    #     return data

    # к юзеру просто так не обратиться тк дефольное значение
    def validate(self, data):
        if self.context['request'].user != data.get('author'):
            return data
        raise serializers.ValidationError(
            'Нельзя подписаться на себя'
        )
