#!/usr/bin/env python3
"""
This script replaces the default ``flask`` cli to use Flask Unchained's AppFactory

USAGE:
flask [--env=dev|prod|staging|test] [--no-warn] COMMAND <args> [OPTIONS]
"""
import argparse
import flask.cli as flask_cli
import os
import sys
import time

from flask.cli import with_appcontext  # alias this here
from flask_unchained import AppFactory, click
from flask_unchained.app_factory import _load_unchained_config
from flask_unchained.constants import DEV, PROD, STAGING, TEST
from flask_unchained.utils import get_boolean_env
from traceback import format_exc

from .click import GroupOverrideMixin


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


def _should_create_basic_app(env):
    try:
        _load_unchained_config(env)
        return False
    except ImportError:
        return True


def cli_create_app(_):
    # Flask's default click integration silences exceptions thrown by
    # create_app, which IMO isn't so awesome. so this gets around that.
    env = os.getenv('FLASK_ENV')

    if _should_create_basic_app(env):
        return AppFactory.create_basic_app()

    try:
        return AppFactory.create_app(env)
    except:
        print(format_exc())
        clear_env_vars()
        sys.exit(1)


class AppGroupMixin(GroupOverrideMixin):
    def group(self, *args, **kwargs):
        """
        A group allows a command to have subcommands attached.  This is the
        most common way to implement nesting in Click.

        :param name: the name of the group (optional)
        :param commands: a dictionary of commands.
        """
        return super().group(
            *args, cls=kwargs.pop('cls', AppGroup) or AppGroup, **kwargs)


class FlaskGroup(AppGroupMixin, flask_cli.FlaskGroup):
    """
    Top-level click group class for all Flask commands.

    Automatically makes the app context available to commands, using
    :meth:`~flask.cli.with_appcontext`.
    """


class AppGroup(AppGroupMixin, flask_cli.AppGroup):
    """
    Click group class for all Flask subcommands.

    Automatically makes the app context available to commands, using
    :meth:`~flask.cli.with_appcontext`.
    """


@click.group(cls=FlaskGroup, add_default_commands=False,
             help='A utility script for Flask Unchained')
@click.option('--env', default=os.getenv('FLASK_ENV', DEV),
              type=click.Choice(ENV_CHOICES),
              help='Which env to run in (dev by default).')
@click.option('--warn/--no-warn', default=True,
              help='Whether or not to warn if not running in prod/staging.')
@click.pass_context
def cli(ctx, env, warn):
    ctx.obj.data['env'] = env
    if env in PROD_ENVS and warn:
        production_warning(env, [arg for arg in sys.argv[1:]
                                 if '--env' not in arg])


@click.group(cls=FlaskGroup, add_default_commands=False,
             help='A utility script for Flask Unchained')
@click.option('--env', default=os.getenv('FLASK_ENV', DEV),
              type=click.Choice(ENV_CHOICES),
              help='Which env to run in (dev by default).')
def basic_cli(env):
    pass


def production_warning(env, args):
    if len(args):
        cmd = ' '.join(args)
        # allow some time to cancel commands
        for i in [3, 2, 1]:
            click.echo(f'!! {env.upper()} !!: Running "{cmd}" in {i} seconds')
            time.sleep(1)


def _get_main_cli():
    # deferred imports to not cause circular dependencies
    from flask_unchained.commands import (
        clean, lint, new, qtconsole, shell, unchained, url, urls)

    cli.add_command(clean)
    cli.add_command(lint)
    cli.add_command(new)
    if qtconsole:
        cli.add_command(qtconsole)
    cli.add_command(flask_cli.run_command)
    cli.add_command(shell)
    cli.add_command(unchained)
    cli.add_command(url)
    cli.add_command(urls)
    return cli


def _get_basic_cli():
    from flask_unchained.commands import new

    basic_cli.add_command(new)
    return basic_cli


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

    if _should_create_basic_app(env):
        cli = _get_basic_cli()
    else:
        cli = _get_main_cli()

    # make sure to always load the app. this is necessary because some 3rd party
    # extensions register commands using setup.py, which for some reason
    # bypasses this step
    obj = flask_cli.ScriptInfo(create_app=cli_create_app)
    obj.load_app()

    cli.main(args=[arg for arg in sys.argv[1:] if '--env' not in arg], obj=obj)
    clear_env_vars()


if __name__ == '__main__':
    main()
