from flask import Flask
from flask_unchained import AppFactoryHook


class RegisterSessionModelHook(AppFactoryHook):
    """
    If using the ``sqlalchemy`` ``SESSION_TYPE``, registers the ``Session`` model with
    the SQLAlchemy Bundle.
    """

    bundle_module_name = None
    name = 'register_session_model'
    run_after = ['init_extensions', 'models']

    def run_hook(self, app: Flask, bundles):
        self.app = app
        if app.config.SESSION_TYPE != 'sqlalchemy':
            return

        Session = app.session_interface.sql_session_model
        self.unchained.sqlalchemy_bundle.models[Session.__name__] = Session

    def update_shell_context(self, ctx: dict):
        if ('sqlalchemy_bundle' in self.unchained.bundles
                and self.app.config.SESSION_TYPE == 'sqlalchemy'):
            ctx.update(self.unchained.sqlalchemy_bundle.models)
