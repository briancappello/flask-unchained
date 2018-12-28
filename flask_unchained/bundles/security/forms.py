import inspect

from flask import current_app as app, request
from flask_unchained.bundles.controller.utils import _validate_redirect_url
from flask_unchained.bundles.sqlalchemy import ModelForm
from flask_unchained import unchained, lazy_gettext as _
from wtforms import (Field, HiddenField, StringField, SubmitField, ValidationError,
                     fields, validators)

from .models import User
from .services import SecurityUtilsService, UserManager
from .utils import current_user

user_manager: UserManager = unchained.get_local_proxy('user_manager')
security_utils_service: SecurityUtilsService = \
    unchained.get_local_proxy('security_utils_service')


password_required = validators.DataRequired(
    _('flask_unchained.bundles.security:password_required'))

password_equal = validators.EqualTo('password', message=_(
    'flask_unchained.bundles.security:error.retype_password_mismatch'))

new_password_equal = validators.EqualTo('new_password', message=_(
    'flask_unchained.bundles.security:error.retype_password_mismatch'))


def unique_user_email(form, field):
    if user_manager.get_by(email=field.data) is not None:
        raise ValidationError(
            _('flask_unchained.bundles.security:error.email_already_associated',
              email=field.data))


def valid_user_email(form, field):
    form.user = user_manager.get_by(email=field.data)
    if form.user is None:
        raise ValidationError(
            _('flask_unchained.bundles.security:error.user_does_not_exist'))


class BaseForm(ModelForm):
    class Meta:
        abstract = True
        only = ()

    def __init__(self, *args, **kwargs):
        if app.testing:
            self.TIME_LIMIT = None
        super().__init__(*args, **kwargs)


class NextFormMixin:
    next = HiddenField()

    def validate_next(self, field):
        if field.data and not _validate_redirect_url(field.data):
            field.data = ''
            raise ValidationError(
                _('flask_unchained.bundles.security:error.invalid_next_redirect'))


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

        if not self.next.data:
            self.next.data = request.args.get('next', '')
        self.remember.default = app.config.SECURITY_DEFAULT_REMEMBER_ME

    def validate(self):
        if not super().validate():
            # FIXME-identity
            if (set(self.errors.keys()) -
                    set(security_utils_service.get_identity_attributes())):
                return False

        self.user = security_utils_service.user_loader(self.email.data)

        if self.user is None:
            self.email.errors.append(
                _('flask_unchained.bundles.security:error.user_does_not_exist'))
            return False
        elif not self.password.data:
            self.password.errors.append(
                _('flask_unchained.bundles.security:password_required'))
            return False
        elif not security_utils_service.verify_password(self.user, self.password.data):
            self.password.errors.append(
                _('flask_unchained.bundles.security:error.invalid_password'))
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
        _('flask_unchained.bundles.security:form_field.password'),
        validators=[password_required])
    password_confirm = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.retype_password'),
        validators=[password_equal, password_required])


class ChangePasswordForm(BaseForm):
    class Meta:
        model = User
        model_fields = {'new_password': 'password',
                        'new_password_confirm': 'password'}

    password = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.password'),
        validators=[password_required])
    new_password = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.new_password'),
        validators=[password_required])
    new_password_confirm = fields.PasswordField(
        _('flask_unchained.bundles.security:form_field.retype_password'),
        validators=[new_password_equal, password_required])

    submit = fields.SubmitField(
        _('flask_unchained.bundles.security:form_submit.change_password'))

    def validate(self):
        result = super().validate()

        if not security_utils_service.verify_password(current_user, self.password.data):
            self.password.errors.append(
                _('flask_unchained.bundles.security:error.invalid_password'))
            return False
        elif self.password.data == self.new_password.data:
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
