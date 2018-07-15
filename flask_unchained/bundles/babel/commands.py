import click
import flask_unchained
import os
import sys

from babel.messages.frontend import CommandLineInterface


@click.group()
def babel():
    """Flask Babel Bundle commands"""


@babel.command()
@click.option('--domain', '-d', default='messages')
def extract(domain):
    """extract messages"""
    translations_dir = os.path.join(os.getcwd(), 'translations')
    if not os.path.exists(translations_dir):
        os.makedirs(translations_dir, exist_ok=True)

    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(flask_unchained.__file__)))
    return _run(f'extract -F {base_dir}/babel.cfg -o translations/{domain}.pot .')


@babel.command()
@click.argument('lang')
@click.option('--domain', '-d', default='messages')
def init(lang, domain):
    """init language translations"""
    return _run(f'init -i translations/{domain}.pot -d translations -l {lang}')


@babel.command()
@click.option('--domain', '-d', default='messages')
def compile(domain):
    """compile translations"""
    return _run(f'compile --directory=translations --domain={domain}')


@babel.command()
@click.option('--domain', '-d', default='messages')
def update(domain):
    """update translations"""
    return _run(f'update -i translations/{domain}.pot -d translations --domain={domain}')


def _run(str):
    return CommandLineInterface().run([sys.argv[0]] + str.split(' '))
