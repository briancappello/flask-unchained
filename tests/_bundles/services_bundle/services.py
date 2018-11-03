from flask_unchained import BaseService, injectable, unchained


class OneService(BaseService):
    """one_service"""
    def __init__(self):
        """one_service __init__"""
        self.bundle = 'services'


class TwoService(BaseService):
    """two_service"""
    def __init__(self, one_service: OneService = injectable):
        """two_service __init__"""
        self.one_service = one_service


class ThreeService(BaseService):
    pass


class FourService(BaseService):
    pass


class FunkyService(BaseService):
    """funky_service"""
    @unchained.inject()
    def __init__(self, two_service: TwoService = injectable):
        """funky_service __init__"""
        self.two_service = two_service

    @unchained.inject('one_service')
    def explicit_funky(self, one_service: OneService = injectable,
                       two_service: TwoService = injectable):
        """explicit_funky"""
        return one_service, two_service

    @unchained.inject()
    def implicit_funky(self, one_service: OneService = injectable,
                       two_service: TwoService = injectable):
        """implicit funky"""
        return one_service, two_service


class ClassAttrService(BaseService):
    one_service: OneService = injectable
    two_service: TwoService = injectable


class ExtendedClassAttrService(ClassAttrService):
    funky_service: FunkyService = injectable


class ClassAttrServiceWithInit(BaseService):
    one_service: OneService = injectable
    two_service: TwoService = injectable

    def __init__(self, funky_service: FunkyService = injectable):
        self.funky_service = funky_service


class ExtendedClassAttrWithInit(ClassAttrServiceWithInit):
    three_service: ThreeService = injectable

    def __init__(self, four_service: FourService = injectable):
        super().__init__()
        self.four_service: FourService = four_service


@unchained.inject()
class NotAutomatic:
    one_service: OneService = injectable


@unchained.inject()
class NotAutomaticWithInit:
    one_service: OneService = injectable

    def __init__(self, two_service: TwoService = injectable):
        self.two_service = two_service


# when not adding any new injectable class attrs, should not need to decorate here
class NotAutomaticExtended(NotAutomatic):
    pass


# when adding new injectable class attrs, the extended class must be wrapped with
# unchained.inject() again, because class decorators do not work with inheritance
@unchained.inject()
class NotAutomaticWithInitExtended(NotAutomaticWithInit):
    funky_service: FunkyService = injectable


class InjectableMethods(BaseService):
    def __init__(self):
        self.one_service = 'constructor_default'
        self.two_service = 'constructor_default'

    def one(self, one_service: OneService = injectable):
        self.one_service = one_service

    def two(self, two_service: TwoService = injectable):
        self.two_service = two_service


@unchained.inject()
class NotAutomaticInjectableMethods:
    def __init__(self):
        self.one_service = 'constructor_default'
        self.two_service = 'constructor_default'

    def one(self, one_service: OneService = injectable):
        self.one_service = one_service

    def two(self, two_service: TwoService = injectable):
        self.two_service = two_service
