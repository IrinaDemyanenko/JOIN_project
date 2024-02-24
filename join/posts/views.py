from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse('Home page')  #главная страница


def group_posts(request, post_slug):
    return HttpResponse('Group posts')
