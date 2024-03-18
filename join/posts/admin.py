from django.contrib import admin
from .models import Post, Group

# класс ModelAdmin связывается с моделью и конфигурирует 
# отображение данных этой модели. В этом классе можно настроить 
# параметры отображения.
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'anons', 'text', 'pub_date',
                    'author', 'group',)
    list_editable = ('group',)
    # Перечислили поля, которые должны отображаться в админке
    search_fields = ('title', 'anons', 'text')
    # Добавляем интерфейс для поиска по тексту постов, заголовку и анонсу
    list_filter = ('pub_date',)
    # Добавляем возможность фильтрации по дате
    empty_value_display = 'Нет записи'
    # Это свойство сработает для всех колонок: 
    # где пусто — там будет эта строка
    
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Post, PostAdmin)
# При регистрации модели Post источником конфигурации для неё назначаем
# класс PostAdmin
admin.site.register(Group)
