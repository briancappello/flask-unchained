from flask_unchained.cli import click


@click.group()
def new():
    """
    Generate new code for your Flask Unchained projects.
    """
