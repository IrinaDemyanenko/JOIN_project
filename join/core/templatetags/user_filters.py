from django import template
# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# добавляем к ним и наш фильтр.
register = template.Library()


# синтаксис @register... , под который описана функция addclass() -
# это применение "декораторов", функций, меняющих поведение функций
@register.filter
def addclass(field, css):  # фильтр будет добавлять в тэг CSS-класс
    return field.as_widget(attrs={'class': css})
    # виджет - это шаблон по которому генерируется HTML код поля формы
    # У объекта field есть метод as_widget().
    # Ему можно передать параметр с перечнем HTML-атрибутов,
    # которые мы хотим изменить.
