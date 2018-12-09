from alembic import command as alembic
from flask.cli import with_appcontext
from flask_migrate.cli import db
from flask_unchained import click, unchained

maybe_fixtures_command = db.command
try:
    from py_yaml_fixtures import FixturesLoader
    from py_yaml_fixtures.factories.sqlalchemy import SQLAlchemyModelFactory
except ImportError:
    # disable the import-fixtures command if py_yaml_fixtures isn't installed
    maybe_fixtures_command = lambda *a, **kw: lambda fn: None

from .extensions import SQLAlchemyUnchained, migrate

db_ext: SQLAlchemyUnchained = unchained.get_local_proxy('db')


@db.command('drop')
@click.option('--force', is_flag=True, expose_value=True,
              prompt='Drop DB tables?')
@with_appcontext
def drop_command(force):
    """Drop database tables."""
    if not force:
        exit('Cancelled.')

    click.echo('Dropping DB tables.')
    drop_all()

    click.echo('Done.')


def drop_all():
    db_ext.drop_all()
    db_ext.engine.execute('DROP TABLE IF EXISTS alembic_version;')


@db.command('reset')
@click.option('--force', is_flag=True, expose_value=True,
              prompt='Drop DB tables and run migrations?')
@with_appcontext
def reset_command(force):
    """Drop database tables and run migrations."""
    if not force:
        exit('Cancelled.')

    click.echo('Dropping DB tables.')
    drop_all()

    click.echo('Running DB migrations.')
    alembic.upgrade(migrate.get_config(None), 'head')

    click.echo('Done.')
