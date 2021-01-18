from flask_unchained.bundles.admin import ModelAdmin, macro
from flask_unchained.bundles.admin.forms import ReorderableForm
from flask_unchained.bundles.security.forms import unique_user_email
from flask_unchained.forms import fields, validators
from flask_unchained.utils import utcnow

from ..models import User

password_length = validators.Length(
    8, message='Password must be at least 8 characters long.')


class BaseUserForm(ReorderableForm):
    def populate_obj(self, user):
        super().populate_obj(user)
        if user.is_active and not user.confirmed_at:
            user.confirmed_at = utcnow()


class UserAdmin(ModelAdmin):
    model = User

    name = 'Users'
    category_name = 'Security'
    menu_icon_value = 'fa fa-user'

    column_list = ('email', 'is_active')
    column_searchable_list = ('email',)
    column_filters = ('is_active',)

    column_details_list = ('email', 'is_active', 'confirmed_at', 'created_at', 'updated_at')
    column_editable_list = ('is_active',)

    column_formatters = {
        'confirmed_at': macro('column_formatters.datetime'),
        'created_at': macro('column_formatters.datetime'),
        'updated_at': macro('column_formatters.datetime'),
    }

    form_base_class = BaseUserForm

    form_columns = ('email', 'roles', 'is_active')
    form_excluded_columns = ('password', 'user_roles')

    form_overrides = dict(email=fields.EmailField)
    form_args = dict(email={'validators': [validators.DataRequired(),
                                           validators.Email()]},
                     roles={'get_label': lambda role: role.name})

    def get_create_form(self):
        CreateForm = super().get_create_form()

        CreateForm.email = fields.EmailField(
            'Email',
            validators=[
                validators.DataRequired(),
                validators.Email(),
                unique_user_email,
            ],
        )
        CreateForm.password = fields.PasswordField(
            'Password',
            validators=[
                validators.DataRequired(),
                password_length,
            ],
        )
        CreateForm.confirm_password = fields.PasswordField(
            'Confirm Password',
            validators=[
                validators.DataRequired(),
                validators.EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
            ],
        )

        CreateForm.field_order = (
            'email', 'password', 'confirm_password', 'roles', 'is_active')

        return CreateForm
