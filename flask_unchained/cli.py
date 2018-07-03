#!/usr/bin/env python
"""
This script replaces the default flask cli to use flask unchained

USAGE:
flask [--env=dev|prod] [--no-warn] COMMAND [OPTIONS] [ARGS]
"""
import argparse
import click
import os
import sys
import time

from flask.cli import FlaskGroup, ScriptInfo, run_command
from flask_unchained import AppFactory
from flask_unchained.commands import clean, lint, qtconsole, shell, unchained, url, urls
from flask_unchained.constants import DEV, PROD, STAGING, TEST
from flask_unchained.utils import get_boolean_env
from traceback import format_exc


ENV_ALIASES = {'dev': DEV, 'prod': PROD}
ENV_CHOICES = list(ENV_ALIASES.keys()) + [DEV, PROD, STAGING, TEST]
PROD_ENVS = {PROD, STAGING}

SHOULD_CLEAR_FLASK_ENV = 'FLASK_ENV' not in os.environ
SHOULD_CLEAR_DEBUG_ENV = 'FLASK_DEBUG' not in os.environ


def clear_env_vars():
    if SHOULD_CLEAR_FLASK_ENV:
        os.environ.pop('FLASK_ENV', None)
    if SHOULD_CLEAR_DEBUG_ENV:
        os.environ.pop('FLASK_DEBUG', None)


def cli_create_app(_):
    # Flask's default click integration silences exceptions thrown by
    # create_app, which IMO isn't so awesome. so this gets around that.
    try:
        return AppFactory.create_app(os.getenv('FLASK_ENV'))
    except:
        print(format_exc())
        clear_env_vars()
        sys.exit(1)


@click.group(cls=FlaskGroup,
             add_default_commands=False,
             help='A utility script for Flask')
@click.option('--env', default=os.getenv('FLASK_ENV', DEV),
              type=click.Choice(ENV_CHOICES),
              help='Which env config to run with (dev by default)')
@click.option('--warn/--no-warn', default=True,
              help='Whether or not to warn if not running in dev')
@click.pass_context
def cli(ctx, env, warn):
    ctx.obj.data['env'] = env
    if env in PROD_ENVS and warn:
        production_warning(env, [arg for arg in sys.argv[1:]
                                 if '--env' not in arg])


def production_warning(env, args):
    if len(args):
        cmd = ' '.join(args)
        # allow some time to cancel commands
        for i in [3, 2, 1]:
            click.echo(f'!! {env.upper()} !!: Running "{cmd}" in {i} seconds')
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--env')
    args, _ = parser.parse_known_args()

    env = args.env or os.getenv('FLASK_ENV', DEV)
    if env in ENV_ALIASES:
        env = ENV_ALIASES[env]
    os.environ['FLASK_ENV'] = env

    debug = get_boolean_env('FLASK_DEBUG', env not in PROD_ENVS)
    os.environ['FLASK_DEBUG'] = 'true' if debug else 'false'

    cli.add_command(clean)
    cli.add_command(lint)
    if qtconsole:
        cli.add_command(qtconsole)
    cli.add_command(run_command)
    cli.add_command(shell)
    cli.add_command(unchained)
    cli.add_command(url)
    cli.add_command(urls)

    # make sure to always load the app. this is necessary because some 3rd party
    # extensions register commands using setup.py, which for some reason
    # bypasses this step
    obj = ScriptInfo(create_app=cli_create_app)
    obj.load_app()

    cli.main(args=[arg for arg in sys.argv[1:] if '--env' not in arg], obj=obj)
    clear_env_vars()


if __name__ == '__main__':
    main()
