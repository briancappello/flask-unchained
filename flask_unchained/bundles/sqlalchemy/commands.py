from alembic import command as alembic
from flask.cli import with_appcontext
from flask_migrate.cli import db
from flask_unchained import click, unchained
from flask_unchained.bundles.sqlalchemy.hooks import ModelFixtureFoldersHook

maybe_fixtures_command = db.command
try:
    from py_yaml_fixtures import FixturesLoader
    from py_yaml_fixtures.factories import SQLAlchemyModelFactory
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


@maybe_fixtures_command(name='import-fixtures')
@click.argument('bundles', nargs=-1,
                help='Bundle names to load from (defaults to all)')
@with_appcontext
def import_fixtures(bundles=None):
    fixture_dirs = []
    for bundle_name in (bundles or unchained.bundles.keys()):
        fixtures_dir = ModelFixtureFoldersHook.get_fixtures_dir(
            unchained.bundles[bundle_name])
        if fixtures_dir:
            fixture_dirs.append(fixtures_dir)

    factory = SQLAlchemyModelFactory(db_ext.session,
                                     unchained.sqlalchemy_bundle.models)
    loader = FixturesLoader(factory, fixture_dirs=fixture_dirs)
    loader.create_all(lambda identifier, model, created: click.echo(
        f'{"Creating" if created else "Updating"} {identifier.key}: {model!r}'))
    click.echo('Finished adding fixtures')
