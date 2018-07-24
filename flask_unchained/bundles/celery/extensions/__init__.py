from .celery import Celery


celery = Celery()


EXTENSIONS = {
    'celery': celery,
}
