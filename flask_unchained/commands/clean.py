# This command is adapted to click from Flask-Script 0.4.0
import os

from flask_unchained.cli import click


@click.command()
def clean():
    """
    Recursively remove \\*.pyc and \\*.pyo files.
    """
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                filepath = os.path.join(dirpath, filename)
                click.echo(f'Removing {filepath}')
                os.remove(filepath)
