from flask_unchained import BaseService, injectable, unchained
from tests._bundles.services_bundle.services import (
    TwoService as BaseTwo, FunkyService as BaseFunky, ClassAttrService as BaseAttrs)


class OneService(BaseService):
    """
    ext one_service
    """
    def __init__(self):
        """
        ext one_service __init__
        """
        self.bundle = 'services_ext'


class TwoService(BaseTwo):
    """
    ext two_service
    """
    def __init__(self, *args, **kwargs):
        """
        ext two_service __init__
        """
        super().__init__(*args, **kwargs)


@unchained.inject()
class FunkyService(BaseFunky):
    """
    ext funky_service
    """
    def __init__(self,
                 one_service: OneService = injectable,
                 two_service: TwoService = injectable):
        """
        ext funky_service __init__
        """
        self.one_service = one_service
        self.two_service = two_service


# this is silly and you shouldn't do this. (but it should work regardless)
@unchained.inject()
class WhyBoth(BaseService):
    """
    why_both
    """
    @unchained.inject()
    def __init__(self, funky_service: FunkyService = injectable):
        """
        why_both __init__
        """
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


class ClassAttrService(BaseAttrs):
    funky_service: FunkyService = injectable
