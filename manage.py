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

sys.path.append(os.getcwd())  # so we can find the user's unchained_config
import unchained_config

from flask.cli import FlaskGroup, run_command
from flask_unchained import DEV, TEST, get_boolean_env
from flask_unchained.commands import clean, lint, shell, unchained, url, urls
from traceback import format_exc


ENV_CHOICES = [env for env in unchained_config.ENV_CONFIGS.keys()
               if env != TEST]

SHOULD_CLEAR_APP_ENV = not bool(os.getenv('FLASK_APP_ENV', None))
SHOULD_CLEAR_DEBUG_ENV = not bool(os.getenv('FLASK_DEBUG', None))


def clear_env_vars():
    if SHOULD_CLEAR_APP_ENV:
        del os.environ['FLASK_APP_ENV']
    if SHOULD_CLEAR_DEBUG_ENV:
        del os.environ['FLASK_DEBUG']


def cli_create_app(_):
    # Flask's default click integration silences exceptions thrown by
    # create_app, which IMO isn't so awesome. so this gets around that.
    try:
        return unchained_config.create_app()
    except:
        print(format_exc())
        clear_env_vars()
        sys.exit(1)


@click.group(cls=FlaskGroup, add_default_commands=False,
             help='A utility script for Flask')
@click.option('--env', default=os.getenv('FLASK_APP_ENV', DEV),
              type=click.Choice(ENV_CHOICES),
              help='Which env config to run with (dev by default)')
@click.option('--warn/--no-warn', default=True,
              help='Whether or not to warn if not running in dev')
@click.pass_context
def cli(ctx, env, warn):
    ctx.obj.data['env'] = env
    if env not in {DEV, TEST} and warn:
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

    env = args.env or os.getenv('FLASK_APP_ENV', DEV)
    os.environ['FLASK_APP_ENV'] = env

    debug = get_boolean_env('FLASK_DEBUG', env in {DEV, TEST})
    if debug:
        os.environ['FLASK_DEBUG'] = 'true'

    cli.add_command(clean)
    cli.add_command(lint)
    cli.add_command(run_command)
    cli.add_command(shell)
    cli.add_command(unchained)
    cli.add_command(url)
    cli.add_command(urls)

    cli.main(args=[arg for arg in sys.argv[1:] if '--env' not in arg])
    clear_env_vars()


if __name__ == '__main__':
    main()
