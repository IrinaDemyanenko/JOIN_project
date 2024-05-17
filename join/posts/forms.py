from django import forms
# Импортируем модуль forms, из него возьмём класс ModelForm
from .models import Contact, Post
# Из этой же директории из файда models.py импортируем класс Contact


class ContactForm(forms.ModelForm):
    # эта форма будет работать с моделью Contact
    class Meta:
        model = Contact
        # Здесь перечислим те поля модели, которые будут отображены
        # в вэб форме
        fields = ('name', 'email', 'subject', 'body',)
        # в основном коде django с моделях auth/forms.py
        # поля перечисляют в круглых скобках


# Создаём класс формы на основе модели Post
class PostForm(forms.ModelForm):
    # эта форма будет работать с моделью Post
    class Meta:
        model = Post
        # Здесь перечислим те поля модели, которые будут отображены
        # в вэб форме
        fields = ('title', 'anons', 'text', 'group',)
        labels = {
            'text': ('текст'),
            'title': ('заголовок'),
            'anons': ('анонс'),
            'group': ('группа')
        }
