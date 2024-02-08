from wtforms import fields

from flask_unchained.bundles.security.forms import RegisterForm as BaseRegisterForm


class RegisterForm(BaseRegisterForm):
    username = fields.StringField("Username")
    first_name = fields.StringField("First Name")
    last_name = fields.StringField("Last Name")
