PORT ?= 8000

install:
	poetry install

lint:
	poetry run flake8 task_manager

collect-ru:
	poetry run django-admin makemessages -l ru

collect-en:
	poetry run django-admin makemessages -l en

compile-texts:
	poetry run django-admin compilemessages

static:
	poetry run python manage.py collectstatic --noinput

2superuser:
	poetry run python manage.py createsuper

migrate:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

dev: migrate
	poetry run python manage.py runserver

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) task_manager.wsgi

test:
	poetry run python3 manage.py test

test-coverage:
	poetry run coverage run manage.py test
	poetry run coverage report -m --include=task_manager/* --omit=task_manager/settings.py,*/migrations/*,*/tests/*,tests.py
	poetry run coverage xml --include=task_manager/* --omit=task_manager/settings.py,*/migrations/*,*/tests/*,tests.py

PHONY: install lint static migrate dev start test