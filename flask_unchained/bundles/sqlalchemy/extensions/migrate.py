import os

from flask_migrate import Migrate as BaseMigrate, Config
from flask_unchained import FlaskUnchained, unchained


class Migrate(BaseMigrate):
    def init_app(self, app: FlaskUnchained):
        alembic_config = app.config.get('ALEMBIC', {})
        alembic_config.setdefault('script_location', 'db/migrations')

        self.configure(Migrate.configure_alembic_template_directory)

        super().init_app(app, db=unchained.extensions.db,
                         directory=alembic_config.get('script_location'),
                         **app.config.get('ALEMBIC_CONTEXT', {}))

    @staticmethod
    def configure_alembic_template_directory(config: Config):
        bundle_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(bundle_root, 'alembic', 'templates')
        setattr(config, 'get_template_directory', lambda: template_dir)
        return config
