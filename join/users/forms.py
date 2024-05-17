from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()
# Функция get_user_model() обращается именно к той модели,
# которая зарегистрирована в качестве основной модели пользователей
# в конфиге проекта.


#  создадим собственный класс для формы регистрации
#  сделаем его наследником предустановленного класса UserCreationForm
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        #  наследуется класс Meta, вложенный в класс UserCreationForm
        # укажем модель, с которой связана создаваемая форма
        model = User
        # тк User = get_user_model(), то по сути model = get_user_model()
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ('first_name', 'last_name', 'username', 'email')
