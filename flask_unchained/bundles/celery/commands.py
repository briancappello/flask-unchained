import subprocess

from flask_unchained.cli import cli


@cli.group()
def celery():
    """
    Celery commands.
    """


@celery.command()
def worker():
    """
    Start the celery worker.
    """
    subprocess.run('celery worker -A celery_app.celery -l debug', shell=True)


@celery.command()
def beat():
    """
    Start the celery beat.
    """
    subprocess.run('celery beat -A celery_app.celery -l debug', shell=True)
