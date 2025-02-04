from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.http import HttpResponse
from django.template import loader

from api.pagination import CustomPagination
from api.throttling import LunchBreakThrottle
from posts.models import Post, Group, User, Comment, Follow
import datetime
from django.core.paginator import Paginator
from posts.forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import JsonResponse

from api.serializer import CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.permissions import IsAuthenticated
from api.permissions import AuthorPermission, IsAuthorOrReadOnly

from rest_framework import filters
from rest_framework.exceptions import ValidationError

class BaseGetPostViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """Базовый класс.
    Позволяет создать новую запись в моделе, получить список записей,
    получить одну запись.
    """
    pass


def get_post(request, pk):
    """Получает пост по переданному pk."""
    if request.method == 'GET':
        # получаем объект публикации по id, он же pk
        post = get_object_or_404(Post, id=pk)
        #post = Post.objects.get(pk=pk)
        # передаём объект публикации сериализатору
        serial_post = PostSerializer(post)
        # View-функция должна вернуть объект JsonResponse с
        # параметром serializer.data
        response = JsonResponse(serial_post.data)
        return response


@api_view(['GET', 'POST'])
def api_posts(request):
    """View-функция API api_posts(), которая будет работать с объектами
    модели Post и обрабатывать только GET- и POST-запросы:
    - в ответ на GET-запрос функция должна возвращать queryset со всеми
    объектами модели Post;
    - при POST-запросе функция должна создавать новый объект и возвращать его.
    """
    # В случае POST-запроса добавим список записей в БД
    # API на вход получает уже готовый JSON от другого API преобразуются
    # в Python-словарь, доступ к которому можно получить через объект
    # request.data. Этот словарь и передаётся в сериализатор через именованный
    # параметр data.
    if request.method == 'POST':
        # Создаём объект сериализатора
        # и передаём в него данные из POST-запроса
        serializer = PostSerializer(data=request.data)
        # Если полученные данные валидны —
        # сохраняем данные в базу через save().
        if serializer.is_valid():
            serializer.save()
            # Возвращаем JSON со всеми данными нового объекта
            # и статус-код 201
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Если данные не прошли валидацию —
        # возвращаем информацию об ошибках и соответствующий статус-код:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # В случае GET-запроса возвращаем список постов
    # Получаем все объекты модели
    posts = Post.objects.all()
    # Передаём queryset в конструктор сериализатора
    serializer = PostSerializer(posts, many=True)
    # В ответ на GET-запрос нужно вернуть JSON
    # Он тоже будет создан из словаря, переданного в Response()
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_post_detail(request, pk):
    """Обрабатывает запросы GET, PUT, PATCH и DELETE.

    Возвращает, перезаписывает, изменяет или удаляет объект модели
    Post по его id.
    """
    try:
        post = Post.objects.get(id=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)

    # Для обновления существующей записи первым параметром
    # в сериализатор передаётся тот объект модели, который
    # нужно обновить. В этом случае вызов save() не приведёт
    # к созданию нового объекта.
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Если данные не прошли валидацию —
        # возвращаем информацию об ошибках и соответствующий статус-код:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Если данные не прошли валидацию —
        # возвращаем информацию об ошибках и соответствующий статус-код:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIPost(APIView):
    """При POST-запросе этот класс должен создавать новый объект
    модели Post и возвращать его, а по GET-запросу должен возвращаться
    сериализованный список всех объектов модели Post.
    """

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class APIPostDetail(APIView):
    """Обрабатывает запросы GET, PUT, PATCH и DELETE:
    возвращает, изменяет или удаляет отдельный объект модели Post."""

    def get(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIGenericPostList(ListCreateAPIView):
    """Возвращает всю коллекцию объектов (например, все посты)
    или может создать новую запись в БД."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class APIGenericPostDetail(RetrieveUpdateDestroyAPIView):
    """Его работа — возвращать, обновлять или удалять объекты модели по одному."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Этот набор представлений предоставит доступ ко всем
    операциям с моделью Post (CRUD). Созданный для него роутер
    будет генерировать два эндпоинта:
    api/v1/posts/, api/v1/posts/<int:pk>/.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # читать могут все, редактировать только автор поста
    permission_classes = [IsAuthorOrReadOnly, ]
    # добавили ограничения на публикации и доступ к ним в обеденное время,
    # ограничения на проект user=100/minute, anon=10/minute
    #throttle_classes = [LunchBreakThrottle, ]
    pagination_class = CustomPagination
    # добавим возможность поиска по тексту по регулярным выражениям
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['$text']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    # def create(self, request):
    #     """Переопределим метод create так, чтобы при создании поста
    #     в качестве автора записывался бы пользователь, полученный из
    #     объекта request.user.
    #     """
    #     if request.method == 'POST':
    #         serializer = PostSerializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save(author=request.user)
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Переопределим метод update так, чтобы редактировать пост мог только
        его автор, делаем проверку в пользователем, полученным из объекта
        request.user.
        """
        post = get_object_or_404(Post, pk=pk)
        if request.user != post.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.method == 'PUT':
            serializer = PostSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """Переопределим метод partial_update так, чтобы редактировать пост мог только
        его автор, делаем проверку в пользователем, полученным из объекта
        request.user.
        """
        post = get_object_or_404(Post, pk=pk)
        if request.user != post.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.method == 'PATCH':
            serializer = PostSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        """Переопределим метод delete так, чтобы редактировать пост мог только
        его автор, делаем проверку в пользователем, полученным из объекта
        request.user.
        """
        post = get_object_or_404(Post, pk=pk)
        if request.user != post.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.method == 'DELETE':
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Группы может создавать только админ сайта, значит доступны только GET
    запросы. Роутер будет генерировать два эндпоинта:
    api/v1/groups/, api/v1/groups/<int:pk>/."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    api/v1/posts/{post_id}/comments/ (GET, POST):
    получаем список всех комментариев поста с id=post_id или создаём новый,
    указав id поста, который хотим прокомментировать;
    api/v1/posts/{post_id}/comments/{comment_id}/ (GET, PUT, PATCH, DELETE):
    получаем, редактируем или удаляем комментарий по id у поста с id=post_id.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, AuthorPermission]

    def perform_create(self, serializer):
        # у экземпляра поста в качестве id берем post_id
        this_post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=this_post)

    # нужно получать не все подряд комментарии, а только относящиеся
    # к посту с переданным id, переопределим метод get_quiryset
    # Тк переопределили объект queryset, в маршрутизаторе становится
    # обязательным параметр basename
    def get_queryset(self):
        # получим пост по id=post_id
        this_post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        # получим список всех комментариев к этому посту
        return this_post.comments.all()


class FollowViewSet(BaseGetPostViewSet):
    """
    ViewSet будет:
    o	возвращает все подписки пользователя, сделавшего запрос;
    o	подписывать пользователя, сделавшего запрос на пользователя,
    переданного в теле запроса.
    """

    serializer_class = FollowSerializer
    # нужно получать не все записи модели Follow, а только
    # относящиеся к id юзера, который делает запрос, показать тех,
    # на кого он подписан
    # Тк переопределили объект queryset, в маршрутизаторе становится
    # обязательным параметр basename
    def get_queryset(self):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        return queryset

    # добавляем возможность поиска по параметру /?search= по полю author
    filter_backends = [filters.SearchFilter, ]
    # искать будем по полю author, которое обращается к модели User к её
    # полю username, т е поиск по полю связанной модели
    # Эту запись читать так: в модели Follow осуществлять поиск по полю author,
    # которое берёт свое значение из модели User поля username
    search_fields = ['author__username', ]

    # переопределим perform_create так, чтобы при попытки пользователя
    # сделавшего запрос подписаться на самого себя, пользователь должен
    # получить информативное сообщение об ошибке
    # поле user может быть использовано на выходе сериализатора
    # (установили дефолтное значение), но без передачи его значения в метод save(),
    # из-за неявного ограничения UniqueTogetherValidator
    # во вьюсете тут уже не обойтись
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    # Анонимный пользователь на запросы к этому эндпоинту должен получать
    # ответ с кодом 401 Unauthorized, воспользуемся разрешениями permissions
    # rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated, ]
