from .celery import Celery


celery = Celery()


EXTENSIONS = {
    'celery': celery,
}


__all__ = [
    'celery',
    'Celery',
]
