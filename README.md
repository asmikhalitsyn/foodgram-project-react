# `Foodgram` - сайт 'Продуктовый помощник'
#### Описание:
 Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное»,
 а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

[![Django-app workflow](https://github.com/asmikhalitsyn/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master)]
(https://github.com/asmikhalitsyn/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

#### Технологии:
- Python
- Django
- Django REST Framework
- PostgreSQL
- Nginx
- Gunicorn
- Docker

### Адрес проекта в облаке

Проект доступен по [адресу](http://51.250.31.177/) 

## Установка Docker
Для запуска проекта на cервере необходимо выполнить следующий ряд действий для операционной системы Ubuntu:
- Сделайте fork репозитория
- После fork'а склонируйте его себе на компьютер
```
git clone https://github.com/<ваш_username>/foodgram-project-react.git
```
- После этого удалите старые версии Docker(при их наличии) командой
```
sudo apt remove docker docker-engine docker.io containerd runc
```
- Обновите индексы пакетов командой 
```
sudo apt update
```
- После обновления индексов установите пакеты которые позволят загружать пакеты по протоколу HTTPS командой
```
sudo apt install \
apt-transport-https \
ca-certificates \
curl gnupg-agent \
software-properties-common -y
```
- Добавьте ключ GPG для подтверждения подлинности в процессе установки командой
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
- Добавьте репозиторий Docker в пакеты apt командой
```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```
- Так как в APT добавлен новый репозиторий необходиом обновить индекс пакетов
```
sudo apt update
```
- Устанавливаем Docker
```
sudo apt install docker-ce docker-compose -y
```
- Далее добавляем команду для запуска демона Docker при старте системы
```
sudo systemctl enable docker
```
## Запуск Docker
Для запуска проекта на локальном компьютере необходио выполнить следующий ряд действий:
- Открываем терминал в склонированной ранее папке
- Создаем образ Docker командой
```
sudo docker build -t <ИМЯ_ВАШЕГО_АККАУНТА>/<ИМЯ_ВАШЕГО_ОБРАЗА_НА_DOCKERHUB>:<ВЕРСИЯ_ВАШЕГО_ОБРАЗА> .
```
- После создания образа загружаем его на DockerHub
```
sudo docker push <ИМЯ_ВАШЕГО_АККАУНТА>/<ИМЯ_ВАШЕГО_ОБРАЗА_НА_DOCKERHUB>:<ВЕРСИЯ_ВАШЕГО_ОБРАЗА>
```
- Заходим на сервер через SSH и устанавлеваем туда Docker
```
sudo apt install docker.io
```
- Если на сервере установлен nginx его необходимо остановить командой
```
sudo systemctl stop nginx
```

Запуск docker-compose

```
docker-compose up -d --build
```

В контейнере выполнить миграции

```
docker-compose exec web python manage.py migrate
```

После создайте суперпользователя

```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec web python manage.py collectstatic --no-input
```

### Автор: [Михалицын Андрей](https://github.com/misterio92)

