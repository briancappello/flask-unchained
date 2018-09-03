from flask import Flask
from flask_unchained import AppFactoryHook


class RegisterSessionModelHook(AppFactoryHook):
    """
    If using ``SESSION_SQLALCHEMY``, register the ``Session`` model with
    the SQLAlchemy Bundle.
    """

    bundle_module_name = None
    run_after = ['init_extensions', 'models']

    def run_hook(self, app: Flask, bundles):
        if app.config.get('SESSION_TYPE') != 'sqlalchemy':
            return

        Session = app.session_interface.sql_session_model
        self.unchained.sqlalchemy_bundle.models['Session'] = Session

    def update_shell_context(self, ctx: dict):
        if ('sqlalchemy_bundle' in self.unchained.bundles
                and 'Session' in self.unchained.sqlalchemy_bundle.models):
            ctx.update(self.unchained.sqlalchemy_bundle.models)
