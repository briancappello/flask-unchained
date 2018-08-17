import inspect

from flask import current_app as app, request
from flask_unchained.bundles.controller.utils import _validate_redirect_url
from flask_unchained.bundles.sqlalchemy import ModelForm
from flask_unchained import unchained, injectable, lazy_gettext as _
from wtforms import (Field, HiddenField, StringField, SubmitField, ValidationError,
                     fields, validators)

from .models import User
from .services import SecurityService, SecurityUtilsService, UserManager
from .utils import current_user


password_equal = validators.EqualTo('password', message=_(
    'flask_unchained.bundles.security:error.retype_password_mismatch'))
new_password_equal = validators.EqualTo('new_password', message=_(
    'flask_unchained.bundles.security:error.retype_password_mismatch'))


@unchained.inject('user_manager')
def unique_user_email(form, field, user_manager: UserManager = injectable):
    if user_manager.get_by(email=field.data) is not None:
        msg = _('flask_unchained.bundles.security:error.email_already_associated',
                email=field.data)
        raise ValidationError(msg)


@unchained.inject('user_manager')
def valid_user_email(form, field, user_manager: UserManager = injectable):
    form.user = user_manager.get_by(email=field.data)
    if form.user is None:
        raise ValidationError(_('flask_unchained.bundles.security:error.user_does_not_exist'))


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        if app.testing:
            self.TIME_LIMIT = None
        super().__init__(*args, **kwargs)


class NextFormMixin:
    next = HiddenField()

    def validate_next(self, field):
        if field.data and not _validate_redirect_url(field.data):
            field.data = ''
            raise ValidationError(_(
                'flask_unchained.bundles.security:error.invalid_next_redirect'))


@unchained.inject('security_service', 'security_utils_service')
class LoginForm(BaseForm, NextFormMixin):
    """The default login form"""
    class Meta:
        model = User

    email = fields.StringField(
        _('flask_unchained.bundles.security:form_field.email'))
    password = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.password'))
    remember = fields.BooleanField(
        _('flask_unchained.bundles.security:form_field.remember_me'))
    submit = fields.SubmitField(
        _('flask_unchained.bundles.security:form_submit.login'))

    def __init__(self, *args,
                 security_service: SecurityService = injectable,
                 security_utils_service: SecurityUtilsService = injectable,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.security_service = security_service
        self.security_utils_service = security_utils_service
        self.user = None

        if not self.next.data:
            self.next.data = request.args.get('next', '')
        self.remember.default = app.config.get('SECURITY_DEFAULT_REMEMBER_ME')

    def validate(self):
        if not super().validate():
            # FIXME-identity
            if (set(self.errors.keys()) -
                    set(self.security_utils_service.get_identity_attributes())):
                return False

        self.user = self.security_utils_service.user_loader(self.email.data)

        if self.user is None:
            self.email.errors.append(
                _('flask_unchained.bundles.security:error.user_does_not_exist'))
            return False
        if not self.user.password:
            self.password.errors.append(
                _('flask_unchained.bundles.security:error.password_not_set'))
            return False
        if not self.security_utils_service.verify_and_update_password(
                self.password.data, self.user):
            self.password.errors.append(
                _('flask_unchained.bundles.security:error.invalid_password'))
            return False
        if (not self.security_service.security.login_without_confirmation
                and self.security_service.security.confirmable
                and self.user.confirmed_at is None):
            self.email.errors.append(
                _('flask_unchained.bundles.security:error.confirmation_required'))
            return False
        if not self.user.active:
            self.email.errors.append(
                _('flask_unchained.bundles.security:error.disabled_account'))
            return False
        return True


class ForgotPasswordForm(BaseForm):
    class Meta:
        model = User

    user = None
    email = StringField(_('flask_unchained.bundles.security:form_field.email'),
                        validators=[valid_user_email])
    submit = fields.SubmitField(
        _('flask_unchained.bundles.security:form_submit.recover_password'))


class PasswordFormMixin:
    password = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.password'))
    password_confirm = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.retype_password'),
        validators=[password_equal])


@unchained.inject('security_utils_service')
class ChangePasswordForm(BaseForm):
    class Meta:
        model = User
        model_fields = {'new_password': 'password',
                        'new_password_confirm': 'password'}

    password = fields.PasswordField(_('flask_unchained.bundles.security:form_field.password'))
    new_password = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.new_password'))
    new_password_confirm = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.retype_password'),
        validators=[new_password_equal])

    submit = fields.SubmitField(_('flask_unchained.bundles.security:form_submit.change_password'))

    def __init__(self, *args, security_utils_service: SecurityUtilsService = injectable,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.security_utils_service = security_utils_service

    def validate(self):
        result = super().validate()

        if not self.security_utils_service.verify_and_update_password(
                self.password.data, current_user):
            self.password.errors.append(
                _('flask_unchained.bundles.security:error.invalid_password'))
            return False
        if self.password.data == self.new_password.data:
            self.new_password.errors.append(
                _('flask_unchained.bundles.security:error.password_is_the_same'))
            return False
        return result


class RegisterForm(BaseForm, PasswordFormMixin, NextFormMixin):
    class Meta:
        model = User

    email = StringField(_('flask_unchained.bundles.security:form_field.email'),
                        validators=[unique_user_email])

    submit = SubmitField(_('flask_unchained.bundles.security:form_submit.register'))

    field_order = ('email', 'password', 'password_confirm', 'submit')

    def to_dict(self):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and hasattr(self.Meta.model, member.name)

        fields = inspect.getmembers(self, is_field_and_user_attr)
        return dict((key, value.data) for key, value in fields)


class ResetPasswordForm(BaseForm, PasswordFormMixin):
    class Meta:
        model = User
        model_fields = {'password_confirm': 'password'}

    submit = SubmitField(
        _('flask_unchained.bundles.security:form_submit.reset_password'))


class SendConfirmationForm(BaseForm):
    class Meta:
        model = User

    user = None
    email = StringField(_('flask_unchained.bundles.security:form_field.email'),
                        validators=[valid_user_email])
    submit = SubmitField(
        _('flask_unchained.bundles.security:form_submit.send_confirmation'))

    def __init__(self, *args, **kwargs):
        super(SendConfirmationForm, self).__init__(*args, **kwargs)
        if request.method == 'GET':
            self.email.data = request.args.get('email', None)

    def validate(self):
        if not super(SendConfirmationForm, self).validate():
            return False
        if self.user.confirmed_at is not None:
            self.email.errors.append(
                _('flask_unchained.bundles.security:error.already_confirmed'))
            return False
        return True
