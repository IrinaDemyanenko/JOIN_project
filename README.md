<<<<<<< HEAD
## Блог-платформа на Django с Api
=======
# Блог-платформа на Django с Api
>>>>>>> 1a1524e524e8fff4f6a25ba24805e4d7daea0e7d
Перед Вами учебный проект блог-платформы или простой социальной сети со встроенным Api,
повторяющим все функции, доступные в вэб-версии приложения.
### Возможности проекта:
1. Анонимный пользователь получает доступ к просмотру новостной ленты - постов зарегистрированных пользователей на главной странице сайта.
2. У каждого поста есть своя страница, простмотр которой так же доступен анонимному пользователю.
3. Посты делятся на категории - группы. Группы может создавать только администартор сайта, пользователи могут отнести свою публикацию к одной из существующих групп.
4. Анонимный пользователь может зарегистрироваться и перейти в новую категорию - пользователь сервиса.
5. Пользователю доступен личный кабинет (prifile), возможность изменить или востановить пароль, а так же выйти из сервиса и перейти в прежнюю категорию - анонимного посетителя.
6. Пользователю доступны те же возможности, что и анонимному посетителю, а так же расширенные функции:
   - создавать/редактировать/удалять посты;
   - по желанию к публикации можно добавить изображение;
   - оставлять комментарии под постами;
   - подписываться на/отписываться от других авторов.


### Возможности API проекта:
* API к проекту создано на базе Django Rest Framework.
* Аутентификация JWT + Djoser. Для обеспечения безопасности проекта, время действия токена ограничено 360 днями. 
* Во избежания повышенной нагрузки на сервер проекта, добавлены ограничения (throttlings):
  - для пользователей: 100 запросов в минуту;
  - для анонимных посетителей: 10 запросов в минуту.
* Для удобства и скорости выдачи ответа, добавлено разбиение выдачи на страницы (pagination): 10 объектов на страницу.
* Настоящее API открытое - доступ разрешен ко всем адресам с префиксом /api/.
* Настроен автоматический способ создания документации Open API, с помощью приложения drf-spectacular.

В настоящий момент доступна единственная версия API, документацию к которой можно подробно изучить, после запуска сервера, по адресам:
1) ..../api/v1/docs/swagger/
2) ..../api/v1/docs/redoc/



### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/IrinaDemyanenko/JOIN_project.git
```

```
cd JOIN_project/join/
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source env/bin/activate
```
или
```
venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
