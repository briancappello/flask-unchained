from flask import Flask
from flask_migrate import Migrate as BaseMigrate
from flask_unchained import unchained, injectable

from .sqlalchemy import SQLAlchemy


class Migrate(BaseMigrate):
    @unchained.inject('db')
    def init_app(self, app: Flask, db: SQLAlchemy = injectable):
        alembic_config = app.config.get('ALEMBIC', {})
        alembic_config.setdefault('script_location', 'db/migrations')

        super().init_app(app, db=db,
                         directory=alembic_config.get('script_location'),
                         **app.config.get('ALEMBIC_CONTEXT', {}))
