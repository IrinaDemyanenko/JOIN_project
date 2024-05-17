from django.shortcuts import render
from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Обрабатывает GET-запросы к странице автора."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Обрабатывает GET-запросы к странице технологии."""
    template_name = 'about/tech.html'
