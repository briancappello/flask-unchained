from flask import Request
from flask_login import LoginManager
from flask_principal import Principal, Identity, UserNeed, RoleNeed, identity_loaded
from flask_unchained import FlaskUnchained, injectable, lazy_gettext as _
from flask_unchained.utils import ConfigProperty, ConfigPropertyMeta
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from types import FunctionType
from typing import *

from ..models import AnonymousUser, User
from ..utils import current_user
from ..services.security_utils_service import SecurityUtilsService
from ..services.user_manager import UserManager


class _SecurityConfigProperties(metaclass=ConfigPropertyMeta):
    __config_prefix__ = 'SECURITY'

    changeable: bool = ConfigProperty()
    confirmable: bool = ConfigProperty()
    login_without_confirmation: bool = ConfigProperty()
    recoverable: bool = ConfigProperty()
    registerable: bool = ConfigProperty()

    token_authentication_header: str = ConfigProperty()
    token_authentication_key: str = ConfigProperty()
    token_max_age: str = ConfigProperty()

    password_hash: str = ConfigProperty()
    password_salt: str = ConfigProperty()

    datetime_factory: FunctionType = ConfigProperty()
    _unauthorized_callback: FunctionType = \
        ConfigProperty('SECURITY_UNAUTHORIZED_CALLBACK')


class Security(_SecurityConfigProperties):
    """
    The `Security` extension::

        from flask_unchained.bundles.security import security
    """

    def __init__(self):
        self._context_processors = {}
        self._send_mail_task = None

        # injected services
        self.security_utils_service = None
        self.user_manager = None

        # remaining properties are all set by `self.init_app`
        self.confirm_serializer = None
        self.hashing_context = None
        self.login_manager = None
        self.login_serializer = None
        self.principal = None
        self.pwd_context = None
        self.remember_token_serializer = None
        self.reset_serializer = None

    def init_app(self, app: FlaskUnchained):
        # NOTE: the order of these `self.get_*` calls is important!
        self.confirm_serializer = self._get_serializer(app, 'confirm')
        self.hashing_context = self._get_hashing_context(app)
        self.login_manager = self._get_login_manager(
            app, app.config.get('SECURITY_ANONYMOUS_USER'))
        self.login_serializer = self._get_serializer(app, 'login')
        self.principal = self._get_principal(app)
        self.pwd_context = self._get_pwd_context(app)
        self.remember_token_serializer = self._get_serializer(app, 'remember')
        self.reset_serializer = self._get_serializer(app, 'reset')

        self.context_processor(lambda: dict(security=_SecurityConfigProperties()))

        # FIXME: should this be easier to customize for end users, perhaps by making
        # FIXME: the function come from a config setting?
        identity_loaded.connect_via(app)(self._on_identity_loaded)
        app.extensions['security'] = self

    def inject_services(self,
                        security_utils_service: SecurityUtilsService = injectable,
                        user_manager: UserManager = injectable):
        self.security_utils_service = security_utils_service
        self.user_manager = user_manager

    ######################################################
    # public api to register template context processors #
    ######################################################

    def context_processor(self, fn):
        """
        Add a context processor that runs for every view with a template in the
        security bundle.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor(None, fn)

    def forgot_password_context_processor(self, fn):
        """
        Add a context processor for the :meth:`SecurityController.forgot_password` view.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor('forgot_password', fn)

    def login_context_processor(self, fn):
        """
        Add a context processor for the :meth:`SecurityController.login` view.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor('login', fn)

    def register_context_processor(self, fn):
        """
        Add a context processor for the :meth:`SecurityController.register` view.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor('register', fn)

    def reset_password_context_processor(self, fn):
        """
        Add a context processor for the :meth:`SecurityController.reset_password` view.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor('reset_password', fn)

    def change_password_context_processor(self, fn):
        """
        Add a context processor for the :meth:`SecurityController.change_password` view.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor('change_password', fn)

    def send_confirmation_context_processor(self, fn):
        """
        Add a context processor for the
        :meth:`SecurityController.send_confirmation_email` view.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor('send_confirmation_email', fn)

    def mail_context_processor(self, fn):
        """
        Add a context processor to be used when rendering all the email templates.

        :param fn: A function that returns a dictionary of template context variables.
        """
        self._add_ctx_processor('mail', fn)

    def run_ctx_processor(self, endpoint) -> Dict[str, Any]:
        rv = {}
        for group in {None, endpoint}:
            for fn in self._context_processors.setdefault(group, []):
                rv.update(fn())
        return rv

    # protected
    def _add_ctx_processor(self, endpoint, fn) -> None:
        group = self._context_processors.setdefault(endpoint, [])
        if fn not in group:
            group.append(fn)

    ##########################################
    # protected api methods used by init_app #
    ##########################################

    def _get_hashing_context(self, app: FlaskUnchained) -> CryptContext:
        """
        Get the token hashing (and verifying) context.
        """
        schemes = app.config.get('SECURITY_HASHING_SCHEMES')
        deprecated = app.config.get('SECURITY_DEPRECATED_HASHING_SCHEMES')
        return CryptContext(
            schemes=schemes,
            deprecated=deprecated)

    def _get_login_manager(self,
                           app: FlaskUnchained,
                           anonymous_user: AnonymousUser,
                           ) -> LoginManager:
        """
        Get an initialized instance of Flask Login's
        :class:`~flask_login.LoginManager`.
        """
        lm = LoginManager()
        lm.anonymous_user = anonymous_user or AnonymousUser
        lm.localize_callback = _
        lm.request_loader(self._request_loader)
        lm.user_loader(
            lambda *a, **kw: self.security_utils_service.user_loader(*a, **kw))
        lm.login_view = 'security_controller.login'
        lm.login_message, _('flask_unchained.bundles.security:error.login_required')
        lm.login_message_category = 'info'
        lm.needs_refresh_message = _(
            'flask_unchained.bundles.security:error.fresh_login_required')
        lm.needs_refresh_message_category = 'info'
        lm.init_app(app)
        return lm

    def _get_principal(self, app: FlaskUnchained) -> Principal:
        """
        Get an initialized instance of Flask Principal's.
        :class:~flask_principal.Principal`.
        """
        p = Principal(app, use_sessions=False)
        p.identity_loader(self._identity_loader)
        return p

    def _get_pwd_context(self, app: FlaskUnchained) -> CryptContext:
        """
        Get the password hashing context.
        """
        pw_hash = app.config.get('SECURITY_PASSWORD_HASH')
        schemes = app.config.get('SECURITY_PASSWORD_SCHEMES')
        deprecated = app.config.get('SECURITY_DEPRECATED_PASSWORD_SCHEMES')
        if pw_hash not in schemes:
            allowed = (', '.join(schemes[:-1]) + ' and ' + schemes[-1])
            raise ValueError(
                "Invalid password hashing scheme %r. Allowed values are %s" %
                (pw_hash, allowed))
        return CryptContext(
            schemes=schemes,
            default=pw_hash,
            deprecated=deprecated)

    def _get_serializer(self, app: FlaskUnchained, name: str) -> URLSafeTimedSerializer:
        """
        Get a URLSafeTimedSerializer for the given serialization context name.

        :param app: the :class:`FlaskUnchained` instance
        :param name: Serialization context. One of ``confirm``, ``login``,
          ``remember``, or ``reset``
        :return: URLSafeTimedSerializer
        """
        secret_key = app.config.get('SECRET_KEY')
        salt = app.config.get('SECURITY_%s_SALT' % name.upper())
        return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)

    def _identity_loader(self) -> Union[Identity, None]:
        """
        Identity loading function to be passed to be assigned to the Principal
        instance returned by :meth:`_get_principal`.
        """
        if not isinstance(current_user._get_current_object(), AnonymousUser):
            identity = Identity(current_user.id)
            return identity

    def _on_identity_loaded(self, sender, identity: Identity) -> None:
        """
        Callback that runs whenever a new identity has been loaded.
        """
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        for role in getattr(current_user, 'roles', []):
            identity.provides.add(RoleNeed(role.name))

        identity.user = current_user

    def _request_loader(self, request: Request) -> Union[User, AnonymousUser]:
        """
        Attempt to load the user from the request token.
        """
        header_key = self.token_authentication_header
        args_key = self.token_authentication_key
        header_token = request.headers.get(header_key, None)
        token = request.args.get(args_key, header_token)
        if request.is_json:
            data = request.get_json(silent=True) or {}
            token = data.get(args_key, token)

        try:
            data = self.remember_token_serializer.loads(
                token, max_age=self.token_max_age)
            user = self.user_manager.get(data[0])
            if user and self.security_utils_service.verify_hash(data[1], user.password):
                return user
        except:
            pass
        return self.login_manager.anonymous_user()
