# foodgram-project-react
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать в формате txt сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Проект использует базу данных PostgreSQL. В проекте доступна система регистрации и авторизации пользователей.


# Уровни доступа пользователей:
**Гость (неавторизованный пользователь)** — может просматривать рецепты на главной, просматривать отдельные страницы рецептов, просматривать страницы пользователей, фильтровать рецепты по тегам, создавать аккаунт.

**Авторизованный пользователь** — может менять пароль, создавать/редактировать/удалять
собственные рецепты, просматривать рецепты на главной, просматривать страницы пользователей, просматривать отдельные страницы рецептов, фильтровать рецепты по тегам, добавлять или удалять рецепты в избранное и просматривать свою страницу избранных рецептов, добавлять или удалять рецепты в список покупок и выгружать файл с количеством необходимых ингридиентов для рецептов из списка покупок, подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок

**Администратор** — может изменять пароль любого пользователя, создавать/блокировать/удалять аккаунты пользователей, редактировать/удалять любые рецепты, добавлять/удалять/редактировать ингредиенты, добавлять/удалять/редактировать теги.


# Технологии
![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) Python 3.7<br/>
![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green) Django 3.2


# Инструкция по запуску
1. Клонируйте репозиторий 
```
git@github.com:AtabekovaEkaterina/foodgram-project-react.git
```
2. В дирктории проекта infa/ создайте файл .env, укажите в файле переменные окружения:
```
SECRET_KEY = 'django-insecure-h6k3y%2*^ic8q1=3=v7a7c=se1pwtwu^srvpqg$1o$o$9aimdz' # секретный ключ 
DEBUG=False # выключаем дебаг
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название контейнера
DB_PORT=5432 # порт для подключения к БД
```
3. Откройте приложение Docker и из директории проекта infa/ запустите docker-compose командой
```
docker-compose up
```
4. Выполните миграции: 
```
docker-compose exec backend python manage.py migrate
```
5. Создайте суперпользователя 
```
docker-compose exec backend python manage.py createsuperuser
```
6. Соберите статику
```
docker-compose exec backend python manage.py collectstatic --no-input
```
7. Теперь приложение доступно по адресу http://localhost
8. Панель администратора доступна по адресу http://localhost/adnin/
9. Добавьте ингредиенты в БД из csv-файла, для этого из директории проекта backend/foodgram_project/ выполните команду
```
docker-compose exec backend python manage.py data_load
```


# Примеры возможных запросов
**GET получить рецепт по id**<br>
`http://localhost/api/recipes/{id}/`
<details><summary>Response 200 удачное выполнение запроса</summary>
{<br>
  "id": 0,<br>
  "tags": [<br>
    {<br>
      "id": 0,<br>
      "name": "Завтрак",<br>
      "color": "#E26C2D",<br>
      "slug": "breakfast"<br>
    }<br>
  ],<br>
  "author": {<br>
    "email": "user@example.com",<br>
    "id": 0,<br>
    "username": "string",<br>
    "first_name": "Вася",<br>
    "last_name": "Пупкин",<br>
    "is_subscribed": false<br>
  },<br>
  "ingredients": [<br>
    {<br>
      "id": 0,<br>
      "name": "Картофель отварной",<br>
      "measurement_unit": "г",<br>
      "amount": 1<br>
    }<br>
  ],<br>
  "is_favorited": true,<br>
  "is_in_shopping_cart": true,<br>
  "name": "string",<br>
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",<br>
  "text": "string",<br>
  "cooking_time": 1<br>
}
</details>

**POST добавление рецепта в избранное**<br>
`http://localhost/api/recipes/{id}/favorite/`
<details><summary>Response 201 рецепт уcпешно добавлен в избранное</summary>
{<br>
  "id": 0,<br>
  "name": "string",<br>
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",<br>
  "cooking_time": 1<br>
}
</details>
<details><summary>Response 400 ошибка добавления в избранное</summary>
{<br>
"errors": "string"<br>
}
</details>
<details><summary>Response 401 пользователь не авторизован</summary>
{<br>
  "detail": "Учетные данные не были предоставлены."<br>
}
</details>


# Workflow для проекта
![image](https://github.com/AtabekovaEkaterina/foodgram-project-react/actions/workflows/foodgram_project.yml/badge.svg)<br/>
Для данного проекта настроен workflow, содержащий 4 задачи (job):
1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) и запуск pytest.
2. Сборка и доставка докер-образа для контейнера backend на Docker Hub.
3. Автоматический деплой проекта на боевой сервер.
4. Отправка уведомления в Telegram о том, что процесс деплоя успешно завершился.

IP развернутого проекта http://84.201.158.250<br/>

Учетные данные superuser django на сервере для входа в панель администратора:<br/>
- username: 
```
super_user
```
- password: 
```
foodgram!
```

# Автор backend
Екатерина Атабекова<br>


