from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Post, Group
# Create your views here.

def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    # Одна строка вместо тысячи слов на SQL:
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию (от больших значений к меньшим)
    context = {
        'posts': posts,
        'title': 'Главная страница'
    }
    return render(request, 'posts/index.html', context)  # главная страница


def all_groups(request):
    inf_groups = ('Здесь будет информация обо всех группах.<br>'
    'Аватар группы и краткое описание её интересов:<br>'
    '- группы будут располагаться одна под другой,<br>'
    '- будет возможность фильтровать группы по названиям,<br>'
    '- автоматическое ранжирование по числу участников группы.')
    title = 'Группы'
    data_groups = {
        'inf_groups': inf_groups,
        'title': title
    }
    return render(request, 'posts/all_groups.html', data_groups)  # список всех групп


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_posts.html', context)
# это не верный синтаксис, но как сделать правильно, чтобы менялись
# страницы для каждой группы, т е принимался аргумент post_slug не знаю
