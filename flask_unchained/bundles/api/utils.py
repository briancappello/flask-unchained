from flask_unchained import request
from marshmallow.exceptions import ValidationError
from marshmallow.schema import UnmarshalResult


# from Flask-RESTful
def unpack(value):
    """
    Return a three tuple of data, code, and headers
    """
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}


def safe_load(serializer, instance=None, partial=False):
    try:
        return serializer.load(request.get_json(),
                               instance=instance,
                               partial=partial)
    except ValidationError as e:
        return UnmarshalResult(None, e.normalized_messages())
