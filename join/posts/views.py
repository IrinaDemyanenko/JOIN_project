from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Post, Group, User
import datetime
from django.core.paginator import Paginator
from .forms import PostForm
from django.contrib.auth.decorators import login_required


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
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_author': posts_author
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
    context = {
        'post': post,
        'posts_count': posts_count
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def post_create(request):
    """Возвращает страницу создания поста для авторизованного пользователя."""
    form = PostForm(request.POST or None)
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
    form = PostForm(request.POST or None, instance=post)
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
