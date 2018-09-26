import re

from sqlalchemy_unchained import BaseValidator, ValidationError
from flask_unchained import lazy_gettext as _
from wtforms.validators import HostnameValidation


class EmailValidator(BaseValidator):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case of a validation error.
    """

    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE)

    def __init__(self, message=None):
        super().__init__(message)
        self.validate_hostname = HostnameValidation(require_tld=True)

    def __call__(self, value):
        super().__call__(value)
        if not value:
            return

        message = self.msg
        if message is None:
            message = _('flask_unchained.bundles.security:email_invalid')

        if not value or '@' not in value:
            raise ValidationError(message)

        user_part, domain_part = value.rsplit('@', 1)

        if not self.user_regex.match(user_part):
            raise ValidationError(message)

        if not self.validate_hostname(domain_part):
            raise ValidationError(message)
