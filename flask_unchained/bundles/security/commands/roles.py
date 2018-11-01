from flask_unchained import unchained
from flask_unchained.cli import cli, click
from flask_unchained.commands.utils import print_table

from .utils import _query_to_role
from ..services import RoleManager

role_manager: RoleManager = unchained.get_local_proxy('role_manager')


@cli.group()
def roles():
    """
    Role commands.
    """


@roles.command(name='list')
def list_roles():
    """
    List roles.
    """
    roles = role_manager.all()
    if roles:
        print_table(['ID', 'Name'], [(role.id, role.name) for role in roles])
    else:
        click.echo('No roles found.')


@roles.command(name='create')
@click.option('--name', prompt='Role name',
              help='The name of the role to create, eg `ROLE_USER`.')
def create_role(name):
    """
    Create a new role.
    """
    role = role_manager.create(name=name)
    if click.confirm(f'Are you sure you want to create {role!r}?'):
        role_manager.save(role, commit=True)
        click.echo(f'Successfully created {role!r}')
    else:
        click.echo('Cancelled.')


@roles.command(name='delete')
@click.argument('query', help='The query to search for a role by. For example, '
                              '`id=5` or `name=ROLE_USER`.')
def delete_role(query):
    """
    Delete a role.
    """
    role = _query_to_role(query)
    if click.confirm(f'Are you sure you want to delete {role!r}?'):
        role_manager.delete(role, commit=True)
        click.echo(f'Successfully deleted {role!r}')
    else:
        click.echo('Cancelled.')
