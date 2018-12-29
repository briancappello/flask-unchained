from datetime import datetime, timezone
from flask import abort
from flask_unchained import BundleConfig
from http import HTTPStatus

from .forms import (
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
    SendConfirmationForm,
)
from .models import AnonymousUser


class AuthenticationConfigMixin(BundleConfig):
    """
    Config options for logging in and out.
    """

    SECURITY_LOGIN_FORM = LoginForm
    """
    The form class to use for the login view.
    """

    SECURITY_DEFAULT_REMEMBER_ME = False
    """
    Whether or not the login form should default to checking the
    "Remember me?" option.
    """

    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']  # FIXME-identity
    """
    List of attributes on the user model that can used for logging in with.
    Each must be unique.
    """

    SECURITY_POST_LOGIN_REDIRECT_ENDPOINT = '/'
    """
    The endpoint or url to redirect to after a successful login.
    """

    SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT = '/'
    """
    The endpoint or url to redirect to after a user logs out.
    """


class ChangePasswordConfigMixin(BundleConfig):
    """
    Config options for changing passwords
    """

    SECURITY_CHANGEABLE = False
    """
    Whether or not to enable change password functionality.
    """

    SECURITY_CHANGE_PASSWORD_FORM = ChangePasswordForm
    """
    Form class to use for the change password view.
    """

    SECURITY_POST_CHANGE_REDIRECT_ENDPOINT = None
    """
    Endpoint or url to redirect to after the user changes their password.
    """

    SECURITY_SEND_PASSWORD_CHANGED_EMAIL = \
        'mail_bundle' in BundleConfig.current_app.unchained.bundles
    """
    Whether or not to send the user an email when their password has been changed.
    Defaults to True, and it's strongly recommended to leave this option enabled.
    """


class EncryptionConfigMixin(BundleConfig):
    """
    Config options for encryption hashing.
    """

    SECURITY_PASSWORD_SALT = 'security-password-salt'
    """
    Specifies the HMAC salt. This is only used if the password hash type is
    set to something other than plain text.
    """

    SECURITY_PASSWORD_HASH = 'bcrypt'
    """
    Specifies the password hash algorithm to use when hashing passwords.
    Recommended values for production systems are ``argon2``, ``bcrypt``,
    or ``pbkdf2_sha512``. May require extra packages to be installed.
    """

    SECURITY_PASSWORD_SINGLE_HASH = False
    """
    Specifies that passwords should only be hashed once. By default, passwords
    are hashed twice, first with SECURITY_PASSWORD_SALT, and then with a random
    salt. May be useful for integrating with other applications.
    """

    SECURITY_PASSWORD_SCHEMES = ['argon2',
                                 'bcrypt',
                                 'pbkdf2_sha512',
                                 # and always the last one...
                                 'plaintext']
    """
    List of algorithms that can be used for hashing passwords.
    """

    SECURITY_PASSWORD_HASH_OPTIONS = {}
    """
    Specifies additional options to be passed to the hashing method.
    """

    SECURITY_DEPRECATED_PASSWORD_SCHEMES = ['auto']
    """
    List of deprecated algorithms for hashing passwords.
    """

    SECURITY_HASHING_SCHEMES = ['sha512_crypt']
    """
    List of algorithms that can be used for creating and validating tokens.
    """

    SECURITY_DEPRECATED_HASHING_SCHEMES = []
    """
    List of deprecated algorithms for creating and validating tokens.
    """


class ForgotPasswordConfigMixin(BundleConfig):
    """
    Config options for recovering forgotten passwords
    """

    SECURITY_RECOVERABLE = False
    """
    Whether or not to enable forgot password functionality.
    """

    SECURITY_FORGOT_PASSWORD_FORM = ForgotPasswordForm
    """
    Form class to use for the forgot password form.
    """

    # reset password (when the user clicks the link from the email sent by forgot pw)
    # --------------

    SECURITY_RESET_PASSWORD_FORM = ResetPasswordForm
    """
    Form class to use for the reset password form.
    """

    SECURITY_RESET_PASSWORD_WITHIN = '5 days'
    """
    Specifies the amount of time a user has before their password reset link
    expires. Always pluralized the time unit for this value. Defaults to 5 days.
    """

    SECURITY_POST_RESET_REDIRECT_ENDPOINT = None
    """
    Endpoint or url to redirect to after the user resets their password.
    """

    SECURITY_INVALID_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'
    """
    Endpoint or url to redirect to if the reset token is invalid.
    """

    SECURITY_EXPIRED_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'
    """
    Endpoint or url to redirect to if the reset token is expired.
    """

    SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT = None
    """
    Endpoint or url to redirect to if a GET request is made to the reset password
    view. Defaults to None, meaning no redirect. Useful for single page apps.
    """

    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = \
        'mail_bundle' in BundleConfig.current_app.unchained.bundles
    """
    Whether or not to send the user an email when their password has been reset.
    Defaults to True, and it's strongly recommended to leave this option enabled.
    """


class RegistrationConfigMixin(BundleConfig):
    """
    Config options for user registration
    """

    SECURITY_REGISTERABLE = False
    """
    Whether or not to enable registration.
    """

    SECURITY_REGISTER_FORM = RegisterForm
    """
    The form class to use for the register view.
    """

    SECURITY_POST_REGISTER_REDIRECT_ENDPOINT = None
    """
    The endpoint or url to redirect to after a user completes the
    registration form.
    """

    SECURITY_SEND_REGISTER_EMAIL = \
        'mail_bundle' in BundleConfig.current_app.unchained.bundles
    """
    Whether or not send a welcome email after a user completes the
    registration form.
    """

    # email confirmation options
    # --------------------------

    SECURITY_CONFIRMABLE = False
    """
    Whether or not to enable required email confirmation for new users.
    """

    SECURITY_SEND_CONFIRMATION_FORM = SendConfirmationForm
    """
    Form class to use for the (re)send confirmation email form.
    """

    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False
    """
    Allow users to login without confirming their email first. (This option
    only applies when :attr:`SECURITY_CONFIRMABLE` is True.)
    """

    SECURITY_CONFIRM_EMAIL_WITHIN = '5 days'
    """
    How long to wait until considering the token in confirmation emails to
    be expired.
    """

    SECURITY_POST_CONFIRM_REDIRECT_ENDPOINT = None
    """
    Endpoint or url to redirect to after the user confirms their email.
    Defaults to :attr:`SECURITY_POST_LOGIN_REDIRECT_ENDPOINT`.
    """

    SECURITY_CONFIRM_ERROR_REDIRECT_ENDPOINT = None
    """
    Endpoint to redirect to if there's an error confirming the user's email.
    """


class TokenConfigMixin(BundleConfig):
    """
    Config options for token authentication.
    """

    SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
    """
    Specifies the query string parameter to read when using token authentication.
    """

    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    """
    Specifies the HTTP header to read when using token authentication.
    """

    SECURITY_TOKEN_MAX_AGE = None
    """
    Specifies the number of seconds before an authentication token expires.
    Defaults to None, meaning the token never expires.
    """


class Config(AuthenticationConfigMixin,
             ChangePasswordConfigMixin,
             EncryptionConfigMixin,
             ForgotPasswordConfigMixin,
             RegistrationConfigMixin,
             TokenConfigMixin,
             BundleConfig):
    """
    Default configuration settings for the Security Bundle.
    """

    SECURITY_ANONYMOUS_USER = AnonymousUser
    """
    Class to use for representing anonymous users.
    """

    SECURITY_UNAUTHORIZED_CALLBACK = lambda: abort(HTTPStatus.UNAUTHORIZED)
    """
    This callback gets called when authorization fails. By default we abort with
    an HTTP status code of 401 (UNAUTHORIZED).
    """

    # make datetimes timezone-aware by default
    SECURITY_DATETIME_FACTORY = lambda: datetime.now(timezone.utc)
    """
    Factory function to use when creating new dates. By default we use
    ``datetime.now(timezone.utc)`` to create a timezone-aware datetime.
    """


class TestConfig(Config):
    """
    Default test settings for the Security Bundle.
    """

    SECURITY_PASSWORD_HASH = 'plaintext'
    """
    Disable password-hashing in tests (shaves about 30% off the test-run time)
    """
