import sys

from flask_unchained import unchained
from flask_unchained.cli import click

from ..services import UserManager, RoleManager

user_manager: UserManager = unchained.get_local_proxy('user_manager')
role_manager: RoleManager = unchained.get_local_proxy('role_manager')


def _query_to_user(query):
    kwargs = _query_to_kwargs(query)
    user = user_manager.get_by(**kwargs)
    if not user:
        click.secho(f'ERROR: Could not locate a user by {_format_query(query)}',
                    fg='white', bg='red')
        sys.exit(1)
    return user


def _query_to_role(query):
    kwargs = _query_to_kwargs(query)
    role = role_manager.get_by(**kwargs)
    if not role:
        click.secho(f'ERROR: Could not locate a role by {_format_query(query)}',
                    fg='white', bg='red')
        sys.exit(1)
    return role


def _query_to_kwargs(query):
    return dict(map(str.strip, pair.split('=')) for pair in query.split(','))


def _format_query(query):
    return ', '.join([f'{k!s}={v!r}'
                      for k, v in _query_to_kwargs(query).items()])
