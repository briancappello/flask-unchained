import subprocess
import sys
import time

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
    _run_until_killed('celery worker -A celery_app.celery -l debug',
                      'celery worker')


@celery.command()
def beat():
    """
    Start the celery beat.
    """
    _run_until_killed('celery beat -A celery_app.celery -l debug',
                      'celery beat')


def _run_until_killed(cmd, kill_proc):
    p = None
    try:
        p = subprocess.Popen(cmd, shell=True)
        while p.poll() is None:
            time.sleep(0.25)
    except KeyboardInterrupt:
        if p is None:
            return sys.exit(1)

        # attempt graceful termination, timing out after 60 seconds
        p.terminate()
        try:
            r = p.wait(timeout=60)
        except subprocess.TimeoutExpired:
            subprocess.run(f'pkill -9 -f {kill_proc!r}', shell=True)
            sys.exit(1)
        else:
            sys.exit(r)
