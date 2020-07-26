#!/usr/bin/env python3
"""
This script replaces the default ``flask`` cli to use Flask Unchained's AppFactory

USAGE:
flask [--env=dev|prod|staging|test] [--no-warn] COMMAND <args> [OPTIONS]
"""
import argparse
import flask.cli as flask_cli
import functools
import os
import sys
import time

from traceback import format_exc
from typing import *

from flask.cli import with_appcontext  # skipcq (alias)
from pyterminalsize import get_terminal_size

from . import click
from .app_factory import AppFactory, maybe_set_app_factory_from_env
from .constants import DEV, PROD, STAGING, ENV_ALIASES, VALID_ENVS
from .utils import get_boolean_env

IterableOfStrings = Union[List[str], Tuple[str, ...]]
IterableOfTuples = Union[List[tuple], Tuple[tuple, ...]]


ENV_CHOICES = list(ENV_ALIASES.keys()) + VALID_ENVS
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
        AppFactory.load_unchained_config(env)
        return False
    except ImportError:
        return True


def cli_create_app(_load_unchained_config=True):
    # Flask's default click integration silences exceptions thrown by
    # create_app, which IMO isn't so awesome. so this gets around that.
    env = os.getenv('FLASK_ENV')

    try:
        return AppFactory().create_app(
            env, _load_unchained_config=_load_unchained_config)
    except:
        print(format_exc())
        clear_env_vars()
        sys.exit(1)


class AppGroupMixin(click.GroupOverrideMixin):
    def group(self, *args, **kwargs):
        """
        A group allows a command to have subcommands attached.  This is the
        most common way to implement nesting in Click.

        :param name: the name of the group (optional)
        :param commands: a dictionary of commands.
        """
        kwargs.setdefault('cls', AppGroup)
        return super().group(*args, **kwargs)


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

    if warn and env in PROD_ENVS:
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
    if args:
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
    if qtconsole:  # skipcq: PYL-W0125
        cli.add_command(qtconsole)
    cli.add_command(flask_cli.run_command)
    cli.add_command(shell)
    cli.add_command(unchained)
    cli.add_command(url)
    cli.add_command(urls)
    return cli


def _get_basic_cli():
    from flask_unchained.commands import clean, lint, new

    basic_cli.add_command(clean)
    basic_cli.add_command(lint)
    basic_cli.add_command(new)
    return basic_cli


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--env')
    args, _ = parser.parse_known_args()

    env = args.env or os.getenv('FLASK_ENV', DEV)
    os.environ['FLASK_ENV'] = ENV_ALIASES.get(env, env)

    debug = get_boolean_env('FLASK_DEBUG', env not in PROD_ENVS)
    os.environ['FLASK_DEBUG'] = 'true' if debug else 'false'

    maybe_set_app_factory_from_env()
    _load_unchained_config = True
    if _should_create_basic_app(env):
        cli = _get_basic_cli()
        _load_unchained_config = False
    else:
        cli = _get_main_cli()

    # make sure to always load the app. this is necessary because some 3rd party
    # extensions register commands using setup.py, which for some reason
    # bypasses this step
    obj = flask_cli.ScriptInfo(create_app=functools.partial(
        cli_create_app, _load_unchained_config=_load_unchained_config))
    obj.load_app()

    cli.main(args=[arg for arg in sys.argv[1:] if '--env' not in arg], obj=obj)
    clear_env_vars()


if __name__ == '__main__':
    main()


# utility function (not used by this script, but placing it here makes imports
# cleaner elsewhere throughout the codebase)
def print_table(column_names: IterableOfStrings,
                rows: IterableOfTuples,
                column_alignments: Optional[IterableOfStrings] = None,
                primary_column_idx: int = 0,
                ) -> None:
    """
    Prints a table of information to the console. Automatically determines if the
    console is wide enough, and if not, displays the information in list form.

    NOTE: Only "simple types" are supported for row values, AND the types must be
          the same within each column. In other words,
          type(row0[i]) == type(rowN[i]) for all rows for all i

    :param column_names: The heading labels
    :param rows: A list of lists
    :param column_alignments: An optional list of strings, using either '<' or '>'
        to specify left or right alignment respectively
    :param primary_column_idx: Used when displaying information in list form,
        to determine which label should be the top-most one. Defaults to the first
        label in ``column_names``.
    """
    header_template = ''
    row_template = ''
    table_width = 0
    type_formatters = {int: 'd', float: 'f', str: 's'}
    types = [type_formatters.get(type(x), 'r') for x in rows[0]]

    alignments = {int: '>', float: '>'}
    column_alignments = (column_alignments or
                         [alignments.get(type(x), '<') for x in rows[0]])

    def get_column_width(idx):
        header_length = len(column_names[idx])
        content_length = max(len(str(row[idx])) for row in rows)
        return (content_length if content_length > header_length
                else header_length)

    for i in range(0, len(column_names)):
        col_width = get_column_width(i)
        header_col_template = f'{{:{col_width}}}'
        col_template = f'{{:{column_alignments[i]}{col_width}{types[i]}}}'
        if i == 0:
            header_template += header_col_template
            row_template += col_template
            table_width += col_width
        else:
            header_template += '  ' + header_col_template
            row_template += '  ' + col_template
            table_width += 2 + col_width

    # check if we can format the table horizontally
    if table_width < get_terminal_size().columns:
        click.echo(header_template.format(*column_names))
        click.echo('-' * table_width)

        for row in rows:
            try:
                click.echo(row_template.format(*row))
            except TypeError as e:
                raise TypeError(f'{e}: {row!r}')

    # otherwise format it vertically
    else:
        max_label_width = max(*[len(label) for label in column_names])
        non_primary_columns = [(i, col) for i, col in enumerate(column_names)
                               if i != primary_column_idx]
        for row in rows:
            type_ = types[primary_column_idx]
            row_template = f'{{:>{max_label_width}s}}: {{:{type_}}}'
            click.echo(row_template.format(column_names[primary_column_idx],
                                           row[primary_column_idx]))
            for i, label in non_primary_columns:
                row_template = f'{{:>{max_label_width}s}}: {{:{types[i]}}}'
                click.echo(row_template.format(label, row[i]))
            click.echo()
