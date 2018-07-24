from flask import Flask
from flask_unchained import AppFactoryHook


class RegisterSessionModelHook(AppFactoryHook):
    bundle_module_name = None
    run_after = ['init_extensions', 'models']

    def run_hook(self, app: Flask, bundles):
        if app.config.get('SESSION_TYPE') != 'sqlalchemy':
            return

        Session = app.session_interface.sql_session_model
        self.unchained.sqlalchemy_bundle.models['Session'] = Session

    def update_shell_context(self, ctx: dict):
        if (self.unchained.sqlalchemy_bundle
                and 'Session' in self.unchained.sqlalchemy_bundle.models):
            ctx.update(self.unchained.sqlalchemy_bundle.models)
