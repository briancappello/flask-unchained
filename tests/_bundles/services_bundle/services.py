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
