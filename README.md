![workflow](https://github.com/elenashipkova/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Foodgram
### Учебный проект

## Описание проекта

Веб-приложение "Продуктовый помощник". Реализован следующий функционал: система аутентификации, создание/обновление и просмотр рецептов, добавление рецептов в избранное и список покупок, выгрузка списка покупок в txt формате, возможность подписки на авторов рецептов.

## Технологии

* Python 3.8.5

* Django 3.0.5

* Django Rest Framework 3.11.0

* Django Rest Framework Simple JWT 4.3.0

* Postgres 12.4

* Gunicorn 20.0.4

* Psycopg2-binary 2.8.6

* Nginx 1.19.3

* Docker 20.10.8

* docker-compose 1.29.2


## Установка

* Клонировать этот репозиторий:

    ```bash
    git clone https://github.com/elenashipkova/foodgram-project-react.git
    ```

* В репозитории на GitHub прописать secrets:

    ```text
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres   # пароль для подключения к БД (установите свой)
    DB_HOST=db   # название сервиса (контейнера)
    DB_PORT=5432   # порт для подключения к БД
    SECRET_KEY=   # ваш секретный ключ
    DEBUG_VALUE=False
    ALLOWED_HOSTS=[*]
    DOCKER_USERNAME, DOCKER_PASSWORD  # имя пользователя и пароль DockerHub для скачивания образа
    USER, HOST, SSH_KEY, PASSPHRASE  # имя и IP-адрес вашего сервера, приватный ssh-ключ, пароль, если используется
    TELEGRAM_TO, TELEGRAM_TOKEN  # ID вашего аккаунта в телеграм, токен вашего бота
    ```

* На удаленном сервере установить Docker и docker-compose:
    
    ```bash
    sudo apt install docker.io
    sudo apt install docker-compose
    ```

* Скопировать файлы docker-compose.yaml и nginx/default.conf из проекта на ваш сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf

* При пуше в GitHub приложение сначала проходит тесты, при условии пуша в ветку master обновляется образ на Docker Hub и автоматически деплоится на сервер (при успешном workflow). Затем нужно подключиться к удаленному серверу и


    1. применить миграции:

    ```bash
    docker-compose exec web python3 manage.py migrate --noinput
    ```

    2. создать суперпользователя:
    
    ```bash
    docker-compose exec web python3 manage.py createsuperuser
    ```

    3. заполнить базу данных:

    ```bash
    docker-compose exec web python3 manage.py loaddata fixtures.json
    ```

## Развернутый проект доступен по адресу: _http://62.84.119.202_

    
## Автор

* Елена Шипкова
