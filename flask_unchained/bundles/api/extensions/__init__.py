from .api import Api
from .marshmallow import Marshmallow


api = Api()
ma = Marshmallow()


EXTENSIONS = {
    'api': api,
    'ma': (ma, ['db']),
}


__all__ = [
    'api',
    'Api',
    'ma',
    'Marshmallow',
]
