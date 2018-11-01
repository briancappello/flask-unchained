from flask_unchained import unchained
from flask_unchained.cli import cli, click
from flask_unchained.commands.utils import print_table

from .utils import _query_to_role, _query_to_user
from ..extensions import Security
from ..services import SecurityService, UserManager

security: Security = unchained.get_local_proxy('security')
security_service: SecurityService = unchained.get_local_proxy('security_service')
user_manager: UserManager = unchained.get_local_proxy('user_manager')


@cli.group()
def users():
    """
    User model commands.
    """


@users.command('list')
def list_users():
    """
    List users.
    """
    users = user_manager.all()
    if users:
        print_table(
            ['ID', 'Email', 'Active', 'Confirmed At'],
            [(user.id,
              user.email,
              'True' if user.active else 'False',
              user.confirmed_at.strftime('%Y-%m-%d %H:%M%z')
                if user.confirmed_at else 'None',
              ) for user in users])
    else:
        click.echo('No users found.')


@users.command('create')
@click.option('--email', prompt='Email address',
              help="The user's email address.")
@click.option('--password', prompt='Password',
              help='The user\'s password.',
              hide_input=True, confirmation_prompt=True)
@click.option('--active/--inactive', prompt='Should user be active?',
              help='Whether or not the new user should be active.',
              default=False, show_default=True)
@click.option('--confirmed-at', prompt='Confirmed at timestamp (or enter "now")',
              help='The date stamp the user was confirmed at (or enter "now") '
                   ' [default: None]',
              default=None, show_default=True)
@click.option('--send-email/--no-email', default=False, show_default=True,
              help='Whether or not to send the user a welcome email.')
def create_user(email, password, active, confirmed_at, send_email):
    """
    Create a new user.
    """
    if confirmed_at == 'now':
        confirmed_at = security.datetime_factory()
    user = user_manager.create(email=email, password=password, active=active,
                               confirmed_at=confirmed_at)
    if click.confirm(f'Are you sure you want to create {user!r}?'):
        security_service.register_user(user, allow_login=False, send_email=send_email)
        user_manager.save(user, commit=True)
        click.echo(f'Successfully created {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('delete')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def delete_user(query):
    """
    Delete a user.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to delete {user!r}?'):
        user_manager.delete(user, commit=True)
        click.echo(f'Successfully deleted {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('set-password')
@click.argument('query', help='The query to search for a user by. For example, `id=5`, '
                              '`email=a@a.com` or `first_name=A,last_name=B`.')
@click.option('--password', prompt='Password',
              help='The new password to assign to the user.',
              hide_input=True, confirmation_prompt=True)
@click.option('--send-email/--no-email', default=False, show_default=True,
              help='Whether or not to send the user a notification email.')
def set_password(query, password, send_email):
    """
    Set a user's password.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to change {user!r}\'s password?'):
        security_service.change_password(user, password, send_email=send_email)
        user_manager.save(user, commit=True)
        click.echo(f'Successfully updated password for {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('confirm')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def confirm_user(query):
    """
    Confirm a user account.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to confirm {user!r}?'):
        if security_service.confirm_user(user):
            click.echo(f'Successfully confirmed {user!r} at '
                       f'{user.confirmed_at.strftime("%Y-%m-%d %H:%M:%S%z")}')
            user_manager.save(user, commit=True)
        else:
            click.echo(f'{user!r} has already been confirmed.')
    else:
        click.echo('Cancelled.')


@users.command('activate')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def activate_user(query):
    """
    Activate a user.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to activate {user!r}?'):
        user.active = True
        user_manager.save(user, commit=True)
        click.echo(f'Successfully activated {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('deactivate')
@click.argument('query', nargs=1, help='The query to search for a user by. For example, '
                                       '`id=5`, `email=a@a.com` or '
                                       '`first_name=A,last_name=B`.')
def deactivate_user(query):
    """
    Deactivate a user.
    """
    user = _query_to_user(query)
    if click.confirm(f'Are you sure you want to deactivate {user!r}?'):
        user.active = False
        user_manager.save(user, commit=True)
        click.echo(f'Successfully deactivated {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('add-role')
@click.option('-u', '--user', help='The query to search for a user by. For example, '
                                   '`id=5`, `email=a@a.com` or '
                                   '`first_name=A,last_name=B`.')
@click.option('-r', '--role', help='The query to search for a role by. For example, '
                                   '`id=5` or `name=ROLE_USER`.')
def add_role_to_user(user, role):
    """
    Add a role to a user.
    """
    user = _query_to_user(user)
    role = _query_to_role(role)
    if click.confirm(f'Are you sure you want to add {role!r} to {user!r}?'):
        user.roles.append(role)
        user_manager.save(user, commit=True)
        click.echo(f'Successfully added {role!r} to {user!r}')
    else:
        click.echo('Cancelled.')


@users.command('remove-role')
@click.option('-u', '--user', help='The query to search for a user by. For example, '
                                   '`id=5`, `email=a@a.com` or '
                                   '`first_name=A,last_name=B`.')
@click.option('-r', '--role', help='The query to search for a role by. For example, '
                                   '`id=5` or `name=ROLE_USER`.')
def remove_role_from_user(user, role):
    """
    Remove a role from a user.
    """
    user = _query_to_user(user)
    role = _query_to_role(role)
    if click.confirm(f'Are you sure you want to remove {role!r} from {user!r}?'):
        user.roles.remove(role)
        user_manager.save(user, commit=True)
        click.echo(f'Successfully removed {role!r} from {user!r}')
    else:
        click.echo('Cancelled.')
