from django import template
# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# добавляем к ним и наш фильтр.
register = template.Library()


@register.filter
def uglify(text):
    new_text = []
    for ind in range(len(text)):
        if ind % 2 == 0:  # четный индекс
            new_text.append(text[ind].upper())
        else:
            new_text.append(text[ind].lower())
    return ''.join([elem for elem in new_text])