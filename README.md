Installation
============

Add google account credentials in [.env.dev](https://github.com/II9tka/garpix/blob/master/.env.dev)

    $ docker-compose -f docker-compose.yml up -d --build
    $ docker-compose -f docker-compose.yml exec django_api python manage.py makemigrations
    $ docker-compose -f docker-compose.yml exec django_api python manage.py migrate
    $ docker-compose -f docker-compose.yml exec django_api python manage.py make_data
    $ docker-compose -f docker-compose.yml exec django_api python manage.py createsuperuser