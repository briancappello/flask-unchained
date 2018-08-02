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

from flask_unchained import AppFactory, click
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


class FlaskGroup(flask_cli.FlaskGroup):
    def __init__(self, *args, **kwargs):
        from .click import _update_ctx_settings
        super().__init__(*args, context_settings=_update_ctx_settings(
            kwargs.pop('context_settings', None)), **kwargs)

    def command(self, *args, **kwargs):
        """
        Commands are the basic building block of command line interfaces in
        Click.  A basic command handles command line parsing and might dispatch
        more parsing to commands nested below it.

        :param name: the name of the command to use unless a group overrides it.
        :param context_settings: an optional dictionary with defaults that are
                                 passed to the context object.
        :param params: the parameters to register with this command.  This can
                       be either :class:`Option` or :class:`Argument` objects.
        :param help: the help string to use for this command.
        :param epilog: like the help string but it's printed at the end of the
                       help page after everything else.
        :param short_help: the short help to use for this command.  This is
                           shown on the command listing of the parent command.
        :param add_help_option: by default each command registers a ``--help``
                                option.  This can be disabled by this parameter.
        :param options_metavar: The options metavar to display in the usage.
                                Defaults to ``[OPTIONS]``.
        :param args_before_options: Whether or not to display the options
                                            metavar before the arguments.
                                            Defaults to False.
        """
        return super().command(
            *args, cls=kwargs.pop('cls', click.Command) or click.Command, **kwargs)

    def group(self, *args, **kwargs):
        """
        A group allows a command to have subcommands attached.  This is the
        most common way to implement nesting in Click.

        :param name: the name of the group (optional)
        :param commands: a dictionary of commands.
        """
        return super().group(
            *args, cls=kwargs.pop('cls', AppGroup) or AppGroup, **kwargs)


class AppGroup(flask_cli.AppGroup):
    def __init__(self, *args, **kwargs):
        from .click import _update_ctx_settings
        super().__init__(*args, context_settings=_update_ctx_settings(
            kwargs.pop('context_settings', None)), **kwargs)

    def command(self, *args, **kwargs):
        """
        Commands are the basic building block of command line interfaces in
        Click.  A basic command handles command line parsing and might dispatch
        more parsing to commands nested below it.

        :param name: the name of the command to use unless a group overrides it.
        :param context_settings: an optional dictionary with defaults that are
                                 passed to the context object.
        :param params: the parameters to register with this command.  This can
                       be either :class:`Option` or :class:`Argument` objects.
        :param help: the help string to use for this command.
        :param epilog: like the help string but it's printed at the end of the
                       help page after everything else.
        :param short_help: the short help to use for this command.  This is
                           shown on the command listing of the parent command.
        :param add_help_option: by default each command registers a ``--help``
                                option.  This can be disabled by this parameter.
        :param options_metavar: The options metavar to display in the usage.
                                Defaults to ``[OPTIONS]``.
        :param args_before_options: Whether or not to display the options
                                            metavar before the arguments.
                                            Defaults to False.
        """
        return super().command(
            *args, cls=kwargs.pop('cls', click.Command) or click.Command, **kwargs)

    def group(self, *args, **kwargs):
        """
        A group allows a command to have subcommands attached.  This is the
        most common way to implement nesting in Click.

        :param name: the name of the group (optional)
        :param commands: a dictionary of commands.
        """
        return super().group(
            *args, cls=kwargs.pop('cls', AppGroup) or AppGroup, **kwargs)


@click.group(cls=FlaskGroup, add_default_commands=False,
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

    # deferred imports to not cause circular dependencies
    from flask_unchained.commands import (
        clean, lint, qtconsole, shell, unchained, url, urls)

    cli.add_command(clean)
    cli.add_command(lint)
    if qtconsole:
        cli.add_command(qtconsole)
    cli.add_command(flask_cli.run_command)
    cli.add_command(shell)
    cli.add_command(unchained)
    cli.add_command(url)
    cli.add_command(urls)

    # make sure to always load the app. this is necessary because some 3rd party
    # extensions register commands using setup.py, which for some reason
    # bypasses this step
    obj = flask_cli.ScriptInfo(create_app=cli_create_app)
    obj.load_app()

    cli.main(args=[arg for arg in sys.argv[1:] if '--env' not in arg], obj=obj)
    clear_env_vars()


if __name__ == '__main__':
    main()
