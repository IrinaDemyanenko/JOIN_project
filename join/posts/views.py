from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Post, Group, User, Comment, Follow
import datetime
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import JsonResponse

from .serializer import PostSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Число в аргументе указывает, сколько секунд надо хранить значение в кеше
@cache_page(20)
# добавила кеширование в шаблон, только список постов, не всю страницу
def index(request):
    # поиск на главной странице
    keyword = request.GET.get('q', None)
    if keyword:  # если слово существует, True
        posts = Post.objects.select_related('author', 'group').filter(
            text__contains=keyword)
        # поля в кавычках 'author', 'group', переменная без кавычек keyword
    else:
        posts = None
        #posts = Post.objects.all().order_by('-pub_date')

    posts_list = Post.objects.all().order_by('-pub_date')
    # Показывать по 10 записей на странице.
    paginator = Paginator(posts_list, 10)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Последние обновления на сайте',
        'posts': posts
    }
    return render(request, 'posts/index.html', context)  # главная страница
    # Вариант1:
    # posts = Post.objects.order_by('-pub_date')[:10]
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию
    # (от больших значений к меньшим)

    # Вариант2:
    # keyword = request.GET.get('q', None)
    # if keyword:  # если слово существует, True
        # posts = Post.objects.select_related('author', 'group').filter(
            # text__contains=keyword)
        # поля в кавычках 'author', 'group', переменная без кавычек keyword
    # else:
        # posts = None


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    # Вариант1 - Выводит по 10 записей на стр. группы
    # group = get_object_or_404(Group, slug=slug)
    # posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    # context = {
        # 'group': group,
        # 'posts': posts,
    # }
    return render(request, 'posts/group_posts.html', context)


def all_groups(request):
    inf_groups = (
        'Здесь будет информация обо всех группах.<br>'
        'Аватар группы и краткое описание её интересов:<br>'
        '- группы будут располагаться одна под другой,<br>'
        '- будет возможность фильтровать группы по названиям,<br>'
        '- автоматическое ранжирование по числу участников группы.'
        )
    title = 'Группы'
    data_groups = {
        'inf_groups': inf_groups,
        'title': title
    }
    return render(request, 'posts/all_groups.html', data_groups)
    # список всех групп


def profile(request, username):
    """На странице профиля будут отображаться все посты автора.
    А так же ник автора.
    """
    author = get_object_or_404(User, username=username)
    # эта запись значит получить из модели User объект с
    # username=username или, если такого нет в базе,
    # вернуть страницу 404
    posts_author = author.posts.all().order_by('-pub_date')
    paginator = Paginator(posts_author, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # тк возможность подписки на автора доступна только
    # зарегистрированным пользователям, нужно проверить,
    # зарегистрирован ли текущий пользователь
    following = request.user.is_authenticated  # если нет, то False
    if following:  # если да, то 
            # нужно проверить есть ли запись в БД модели Follow
            # где user=request.user, author=author
            following = author.following.filter(user=request.user).exists()
            # автор профиля должен иметь связь с моделью Follow, те иметь поле
            # following, в моделе Follow отфильтровать найденные записи по
            # полю user=request.user
            # если такие запист вообще существуют, тогда переменная не будет пустой
            # будет отдавать True
    

    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_author': posts_author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Возвращает конкретный пост автора и кол-во постов,
    написанных автором.
    """
    post = get_object_or_404(Post, id=post_id)  # pk or id
    # эта запись значит получить из модели Post объект с pk=post_id
    # или, если такого нет в базе, вернуть страницу 404
    posts_count = Post.objects.filter(author_id=post.author_id).count()
    comment_form = CommentForm()
    comments = Comment.objects.filter(post_id=post_id) # ?????
    context = {
        'post': post,
        'posts_count': posts_count,
        'comment_form': comment_form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def post_create(request):
    """Возвращает страницу создания поста для авторизованного пользователя."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    # Если получен POST запрос (метод запроса),
    # то создаётся объект (переменная) формы ExchangeForm
    # и передаём в него полученные данные

    # если все данные прошли валидацию
    # работаем с очищенными данными формы
    if form.is_valid():  # True

        # берём очищенные данные из словаря form.cleaned_data
        # title = form.cleaned_data['title']
        # anons = form.cleaned_data['anons']
        # text = form.cleaned_data['text']
        # group = form.cleaned_data['group']
        # в этой функции их не нужно к-л передавать

        # сохраняем объект в БД
        # если данные нужно перд этм как-то обработать, писать здесь

        # пост - это сохранённая заполненная форма
        post = form.save(commit=False) # пока не сохранять новую запись, сначала добавим автора
        # автор поста - это юзер, отправивший запрос
        post.author = request.user
        post.save()  # теперь сохраняем новый пост в БД
        # чтобы защититься от повторного заполнения формы, перенаправляем
        # пользователя на страницу его профайла
        return redirect('posts:profile', post.author)
    # если форма не валидна
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Позволяет отредактироать пост.
    Пост берётся из БД по id.
    Если запрос отправляет автор поста - может отредактировать пост.
    Если запрос отправляет не автор поста - его перенаправляет 
    на страницу детали поста.
    """
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    # post.author == request.user
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post  # передаётся экземпляр формы из БД, т к пост редактируется
        )
    # files=request.FILES or None параметр, отвечающий за то,
    # что форма может работать с файлами
    # instance=post значит, что по умолчанию форма заполняется тем,
    # что уже было в БД
    # потом автор редактирует пост и, если форма валидна, она сохраняется в БД
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True  # редактируется? по умолчанию "да"
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    """Отображает страницу детали поста с формой создания комментария.
    
    Комментарий могут оставить только зарегистрированные пользователи.
    """
    # Получим пост с post_id
    # Если есть пост с таким id, мы его получим, если нет - ошибка 404 
    post = get_object_or_404(Post, pk=post_id)
    # Получим форму создания комментария
    form = CommentForm(request.POST or None)
    if form.is_valid():
        # Комментарий - это пока не сохранённая форма
        comment = form.save(commit=False)
        # автор комм == текущий пользователь,
        # пост комм == полученный по id пост
        comment.author = request.user
        comment.post = post
        comment.save()  #!!!!! не уверена
    # После создания комментария, возвращаем на страницу детали поста
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    """Страница с постами авторов, на которых подписан
    текущий пользователь.
    """
    # получается, читаем с конца: пользователь, который отправляет запрос
    # он же user из модели Follow, найти связанные с ним following,
    # т е тех, на кого он подписан, они же будут являться авторами в
    # модели Post, показать все посты этих авторов
    posts_list = Post.objects.filter(author__following__user=request.user).order_by('-pub_date')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user': request.user,
        'page_obj': page_obj,
        'title': 'Список постов любимых авторов'
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора.
    
    Подписаться можно только на странице профиля автора.
    После подписки, пользователь перенаправляется на страницу
    профиля автора, на которого только что подписался. 
    """
    # проверяем, что автор профиля существует
    author = get_object_or_404(User, username=username)
    # проверяем, что пользователь не является автором профиля
    if request.user != author:
        # чтобы записи не дублировались, проверяем методом get_or_create
        # если такая запись уже есть, дубль не создастся
        # добавляем в БД запись в модель Follow подписчек(user)-автор(author)
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)

@login_required
def profile_unfollow(request, username):
    """Отписаться от автора.
    
    Отписаться можно только на странице профиля автора.
    После отписки, пользователь перенаправляется на страницу
    профиля автора, от которого только что отписался.
    """
    author = get_object_or_404(User, username=username)
    # если пользователь не автор профиля, то ищем запись в БД и
    # удаляем запись из модели Follow
    if request.user != author:
        follower = Follow.objects.get(
            user=request.user,
            author=author
        )
        follower.delete()
    return redirect('posts:profile', username=username)

def get_post(request, post_id):
    """Получает пост по переданному pk."""
    if request.method == 'GET':
        # получаем объект публикации по id, он же pk
        post = get_object_or_404(Post, pk=post_id)
        #post = Post.objects.get(pk=post_id)
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
def api_post_detail(request, post_id):
    """Обрабатывает запросы GET, PUT, PATCH и DELETE.
     
    Возвращает, перезаписывает, изменяет или удаляет объект модели
    Post по его id.
    """
    try:
        post = Post.objects.get(id=post_id)
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
