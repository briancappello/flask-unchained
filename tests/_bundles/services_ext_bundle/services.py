from flask_unchained import BaseService, injectable, unchained
from tests._bundles.services_bundle.services import (
    TwoService, FunkyService as BaseFunky)


class OneService(BaseService):
    """
    ext one_service
    """
    def __init__(self):
        """
        ext one_service __init__
        """
        self.bundle = 'services_ext'


@unchained.inject()
class FunkyService(BaseFunky):
    """
    ext funky_service
    """
    def __init__(self, one_service: OneService = injectable,
                 two_service: TwoService = injectable):
        """
        ext funky service __init__
        """
        self.one_service = one_service
        self.two_service = two_service


# this is silly; you shouldn't do this. (but it should work regardless)
@unchained.inject()
class WhyBoth(BaseService):
    @unchained.inject()
    def __init__(self, funky_service: FunkyService = injectable):
        self.funky_service = funky_service


class ManualInstantiation(BaseService):
    def __init__(self):
        self.foobars = {}

    def foobar(self, name=None):
        def wrapper(fn):
            self.foobars[name or fn.__name__] = fn
            return fn
        return wrapper


manual = ManualInstantiation()
unchained.register_service('manual', manual)


@manual.foobar()
def foobaz():
    return 'foobaz!'
