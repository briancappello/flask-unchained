from typing import *

from flask_unchained import AppFactoryHook, Bundle, FlaskUnchained


class RegisterSessionModelHook(AppFactoryHook):
    """
    If ``app.config.SESSION_TYPE == 'sqlalchemy'``, registers the ``Session``
    model with the SQLAlchemy Bundle.
    """

    bundle_module_names = None
    name = 'register_session_model'
    run_after = ['init_extensions', 'models']

    def run_hook(self,
                 app: FlaskUnchained,
                 bundles: List[Bundle],
                 unchained_config: Optional[Dict[str, Any]] = None,
                 ) -> None:
        self.using_sqlalchemy = app.config.SESSION_TYPE == 'sqlalchemy'
        if not self.using_sqlalchemy:
            return

        if 'sqlalchemy_bundle' not in self.unchained.bundles:
            raise RuntimeError('SESSION_TYPE is configured to use sqlalchemy, '
                               'but the SQLAlchemy Bundle is not enabled!')

        Session = app.session_interface.sql_session_model
        self.unchained.sqlalchemy_bundle.models[Session.__name__] = Session

    def update_shell_context(self, ctx: dict):
        if self.using_sqlalchemy:
            ctx.update(self.unchained.sqlalchemy_bundle.models)
