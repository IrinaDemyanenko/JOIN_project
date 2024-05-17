from django import forms


def validate_not_empty(value):  # Функция-валидатор:
    if value = '':  # если поле пусто
        raise forms.ValidationError(
            "Заполните поле",
            params={'value': value}
        )
