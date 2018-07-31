from .alembic.migrations import render_migration_item


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    db_file = 'db/dev.sqlite'  # relative path to PROJECT_ROOT/db/dev.sqlite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_file}'

    PY_YAML_FIXTURES_DIR = 'db/fixtures'

    ALEMBIC = {
        'script_location': 'db/migrations',
    }

    ALEMBIC_CONTEXT = {
        'render_item': render_migration_item,
        'template_args': {'migration_variables': []},
    }


class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # :memory:
