from flask_unchained.string_utils import title_case
from speaklater import _LazyString
from typing import *


class BaseValidationError(Exception):
    pass


class ValidationError(BaseValidationError):
    """
    holds validation errors for a single column
    """
    def __init__(self, msg: str = None, model=None, column=None, validator=None):
        super().__init__(msg)
        self.msg = msg
        self.model = model
        self.column = column
        self.validator = validator

    def __str__(self):
        if self.validator and hasattr(self.validator, 'get_message'):
            return self.validator.get_message(self)
        return super().__str__()


class ValidationErrors(BaseValidationError):
    """
    holds validation errors for a whole model
    """
    def __init__(self, errors: Dict[str, List[str]]):
        super().__init__()
        self.errors = errors

    def __str__(self):
        return '\n'.join([k + ': ' + str(e) for k, e in self.errors.items()])

def validates(column):
    def decorator(fn):
        fn.__validates__ = column
        return fn
    return decorator


class BaseValidator:
    def __init__(self, msg=None):
        super().__init__()
        self.msg = msg
        self.value = None

    def __call__(self, value):
        self.value = value
        return True

    def get_message(self, e: ValidationError):
        return self.msg


class Required(BaseValidator):
    def __call__(self, value):
        super().__call__(value)
        if value is None or isinstance(value, str) and not value:
            raise ValidationError(validator=self)
        return True

    def get_message(self, e: ValidationError):
        if self.msg:
            if isinstance(self.msg, str):
                return self.msg
            elif isinstance(self.msg, _LazyString):
                return str(self.msg)
        return f'{title_case(e.column)} is required.'
