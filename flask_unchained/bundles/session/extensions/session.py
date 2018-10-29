import dill

from flask_session import Session as BaseSession

from ..session_interfaces import SqlAlchemySessionInterface


class Session(BaseSession):
    """
    The `Session` extension::

        from flask_unchained.bundles.session import session
    """

    def init_app(self, app):
        super().init_app(app)
        app.session_interface.serializer = dill

    def _get_interface(self, app):
        if app.config.SESSION_TYPE == 'sqlalchemy':
            return SqlAlchemySessionInterface(
                db=app.config.SESSION_SQLALCHEMY,
                table=app.config.SESSION_SQLALCHEMY_TABLE,
                key_prefix=app.config.SESSION_KEY_PREFIX,
                use_signer=app.config.SESSION_USE_SIGNER,
                permanent=app.config.SESSION_PERMANENT,
                model_class=app.config.SESSION_SQLALCHEMY_MODEL)
        return super()._get_interface(app)
