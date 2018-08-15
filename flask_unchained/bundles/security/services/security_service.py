from datetime import timedelta
from flask import _request_ctx_stack, current_app as app, session
from flask_login.signals import user_logged_in
from flask_login.utils import _get_user, logout_user as _logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from flask_unchained import url_for, lazy_gettext as _
from flask_unchained.bundles.mail import Mail
from flask_unchained import BaseService, injectable
from typing import *

from .security_utils_service import SecurityUtilsService
from .user_manager import UserManager
from ..extensions import Security
from ..models import User
from ..signals import (confirm_instructions_sent, reset_password_instructions_sent,
                       password_changed, password_reset, user_confirmed, user_registered)


class SecurityService(BaseService):
    def __init__(self,
                 security: Security = injectable,
                 security_utils_service: SecurityUtilsService = injectable,
                 user_manager: UserManager = injectable,
                 mail: Optional[Mail] = None,  # injectable, but optional
                 ):
        self.mail = mail
        self.security = security
        self.security_utils_service = security_utils_service
        self.user_manager = user_manager

    def login_user(self,
                   user: User,
                   remember: Optional[bool] = None,
                   duration: Optional[timedelta] = None,
                   force: bool = False,
                   fresh: bool = True,
                   ) -> bool:
        """
        Logs a user in. You should pass the actual user object to this. If the
        user's `active` property is ``False``, they will not be logged in
        unless `force` is ``True``.

        This will return ``True`` if the log in attempt succeeds, and ``False`` if
        it fails (i.e. because the user is inactive).

        :param user: The user object to log in.
        :type user: object
        :param remember: Whether to remember the user after their session expires.
            Defaults to ``False``.
        :type remember: bool
        :param duration: The amount of time before the remember cookie expires. If
            ``None`` the value set in the settings is used. Defaults to ``None``.
        :type duration: :class:`datetime.timedelta`
        :param force: If the user is inactive, setting this to ``True`` will log
            them in regardless. Defaults to ``False``.
        :type force: bool
        :param fresh: setting this to ``False`` will log in the user with a session
            marked as not "fresh". Defaults to ``True``.
        :type fresh: bool
        """
        if not user.active and not force:
            return False

        if (self.security.confirmable and not user.confirmed_at
                and not self.security.login_without_confirmation):
            return False

        session['user_id'] = getattr(user, user.Meta.pk)
        session['_fresh'] = fresh
        session['_id'] = app.login_manager._session_identifier_generator()

        if remember is None:
            remember = app.config.get('SECURITY_DEFAULT_REMEMBER_ME')
        if remember:
            session['remember'] = 'set'
            if duration is not None:
                try:
                    # equal to timedelta.total_seconds() but works with Python 2.6
                    session['remember_seconds'] = (duration.microseconds +
                                                   (duration.seconds +
                                                    duration.days * 24 * 3600) *
                                                   10 ** 6) / 10.0 ** 6
                except AttributeError:
                    raise Exception('duration must be a datetime.timedelta, '
                                    'instead got: {0}'.format(duration))

        _request_ctx_stack.top.user = user
        user_logged_in.send(app._get_current_object(), user=_get_user())
        identity_changed.send(app._get_current_object(),
                              identity=Identity(user.id))
        return True

    def process_login_errors(self, form):
        """
        An opportunity to modify the login form's error messages before returning
        the response to the user. The idea is to try not to leak excess account info
        without being too unfriendly to actually-valid-users.

        :param form: An instance of the config option `SECURITY_LOGIN_FORM` class.
        """
        account_disabled = _('flask_unchained.bundles.security:error.disabled_account')
        confirmation_required = _('flask_unchained.bundles.security:error.confirmation_required')
        if account_disabled in form.errors.get('email', []):
            error = account_disabled
        elif confirmation_required in form.errors.get('email', []):
            error = confirmation_required
        else:
            identity_attrs = app.config.get('SECURITY_USER_IDENTITY_ATTRIBUTES')
            error = f"Invalid {', '.join(identity_attrs)} and/or password."

        # wipe out all individual field errors, we just want a single form-level error
        form._errors = {'_error': [error]}
        for field in form._fields.values():
            field.errors = None
        return form

    def logout_user(self):
        """
        Logs out the current user and cleans up the remember me cookie (if any).

        Sends signal `identity_changed` (from flask_principal).
        Sends signal `user_logged_out` (from flask_login).
        """

        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)
        identity_changed.send(app._get_current_object(),
                              identity=AnonymousIdentity())
        _logout_user()

    def register_user(self, user, allow_login=None, send_email=None):
        """
        Service method to register a user.

        Sends signal `user_registered`.

        Returns True if the user has been logged in, False otherwise.
        """
        should_login_user = (not self.security.confirmable
                             or self.security.login_without_confirmation)
        should_login_user = (should_login_user if allow_login is None
                             else allow_login and should_login_user)
        if should_login_user:
            user.active = True

        # confirmation token depends on having user.id set, which requires
        # the user be committed to the database
        self.user_manager.save(user, commit=True)

        confirmation_link, token = None, None
        if self.security.confirmable:
            token = self.security_utils_service.generate_confirmation_token(user)
            confirmation_link = url_for('security_controller.confirm_email',
                                        token=token, _external=True)

        user_registered.send(app._get_current_object(),
                             user=user, confirm_token=token)

        if (send_email or (
                send_email is None
                and app.config.get('SECURITY_SEND_REGISTER_EMAIL'))):
            self.send_mail(_('flask_unchained.bundles.security:email_subject.register'),
                           to=user.email,
                           template='security/email/welcome.html',
                           user=user,
                           confirmation_link=confirmation_link)

        if should_login_user:
            return self.login_user(user)
        return False

    def change_password(self, user, password, send_email=None):
        """
        Service method to change a user's password.

        Sends signal `password_changed`.

        :param user: The :class:`User`'s password to change.
        :param password: The new password.
        :param send_email: Whether or not to override the config option
                           ``SECURITY_SEND_PASSWORD_CHANGED_EMAIL`` and force
                           either sending or not sending an email.
        """
        user.password = password
        self.user_manager.save(user)
        if send_email or (app.config.get('SECURITY_SEND_PASSWORD_CHANGED_EMAIL')
                          and send_email is None):
            self.send_mail(
                _('flask_unchained.bundles.security:email_subject.password_changed_notice'),
                to=user.email,
                template='security/email/password_changed_notice.html',
                user=user)
        password_changed.send(app._get_current_object(), user=user)

    def reset_password(self, user, password):
        """
        Service method to reset a user's password. The same as :meth:`change_password`
        except we this method sends a different notification email.

        Sends signal `password_reset`.

        :param user:
        :param password:
        :return:
        """
        user.password = password
        self.user_manager.save(user)
        if app.config.get('SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL'):
            self.send_mail(
                _('flask_unchained.bundles.security:email_subject.password_reset_notice'),
                to=user.email,
                template='security/email/password_reset_notice.html',
                user=user)
        password_reset.send(app._get_current_object(), user=user)

    def send_email_confirmation_instructions(self, user):
        """
        Sends the confirmation instructions email for the specified user.

        Sends signal `confirm_instructions_sent`.

        :param user: The user to send the instructions to.
        """
        token = self.security_utils_service.generate_confirmation_token(user)
        confirmation_link = url_for('security_controller.confirm_email',
                                    token=token, _external=True)
        self.send_mail(
            _('flask_unchained.bundles.security:email_subject.email_confirmation_instructions'),
            to=user.email,
            template='security/email/email_confirmation_instructions.html',
            user=user,
            confirmation_link=confirmation_link)
        confirm_instructions_sent.send(app._get_current_object(), user=user,
                                       token=token)

    def send_reset_password_instructions(self, user):
        """
        Sends the reset password instructions email for the specified user.

        Sends signal `reset_password_instructions_sent`.

        :param user: The user to send the instructions to.
        """
        token = self.security_utils_service.generate_reset_password_token(user)
        reset_link = url_for('security_controller.reset_password',
                             token=token, _external=True)
        self.send_mail(
            _('flask_unchained.bundles.security:email_subject.reset_password_instructions'),
            to=user.email,
            template='security/email/reset_password_instructions.html',
            user=user,
            reset_link=reset_link)
        reset_password_instructions_sent.send(app._get_current_object(),
                                              user=user, token=token)

    def confirm_user(self, user):
        """
        Confirms the specified user. Returns False if the user has already been
        confirmed, True otherwise.

        :param user: The user to confirm.
        """
        if user.confirmed_at is not None:
            return False
        user.confirmed_at = self.security.datetime_factory()
        user.active = True
        self.user_manager.save(user)

        user_confirmed.send(app._get_current_object(), user=user)
        return True

    def send_mail(self, subject, to, template, **template_ctx):
        """
        Utility method to send mail with the `mail` template context.
        """
        if not self.mail:
            from warnings import warn
            warn('Attempting to send mail without the mail bundle installed! '
                 'Please install it, or fix your configuration.')
            return

        self.mail.send(subject, to, template, **dict(
            **self.security.run_ctx_processor('mail'),
            **template_ctx))
