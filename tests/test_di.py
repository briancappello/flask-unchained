import pytest

from flask_unchained import BaseService, injectable, unchained
from flask_unchained.exceptions import ServiceUsageError


def test_injectable():
    class Foo(BaseService):
        def __init__(self, fail=injectable):
            self.fail = fail

    with pytest.raises(ServiceUsageError) as e:
        Foo()
    assert 'Foo was initialized without the fail parameter' in str(e)


@pytest.mark.usefixtures('app')
class TestInject:

    # FIXME this is really a test for the load services hook
    @pytest.mark.bundles(['tests._bundles.services_bundle'])
    def test_it_works(self):
        from tests._bundles.services_bundle.services import (
            OneService, TwoService, FunkyService)
        assert isinstance(unchained.services.one_service, OneService)
        assert isinstance(unchained.services.two_service, TwoService)
        assert isinstance(unchained.services.funky_service, FunkyService)

    # FIXME this is really a test for the load services hook
    @pytest.mark.bundles(['tests._bundles.services_ext_bundle'])
    def test_bundle_overriding_works(self, app):
        from tests._bundles.services_ext_bundle.services import (
            OneService, TwoService, FunkyService)
        assert isinstance(unchained.services.one_service, OneService)
        assert isinstance(unchained.services.two_service, TwoService)
        assert isinstance(unchained.services.funky_service, FunkyService)

    @pytest.mark.bundles(['tests._bundles.services_ext_bundle'])
    def test_it(self):
        from tests._bundles.services_ext_bundle.services import (
            OneService, TwoService, FunkyService, WhyBoth)

        # check correct name, docstrings
        assert getattr(OneService, '__di_name__') == 'one_service'
        assert 'ext one_service' in OneService.__doc__
        assert 'ext one_service __init__' in OneService.__init__.__doc__

        # check correct signature
        cls_sig = getattr(OneService, '__signature__')
        init_sig = getattr(OneService.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self']

        one_service = OneService()
        assert one_service.bundle == 'services_ext'

        # check correct signature
        assert getattr(TwoService, '__di_name__') == 'two_service'
        cls_sig = getattr(TwoService, '__signature__')
        init_sig = getattr(TwoService.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self', 'one_service']

        # check service initialization works without dependency injection
        with pytest.raises(ServiceUsageError) as e:
            unchained.services.pop('one_service')
            TwoService()
        assert 'TwoService was initialized without the one_service' in str(e)

        two_service = TwoService(one_service)
        assert two_service.one_service.bundle == 'services_ext'

        # check correct signature
        assert getattr(FunkyService, '__di_name__') == 'funky_service'
        cls_sig = getattr(FunkyService, '__signature__')
        init_sig = getattr(FunkyService.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self', 'one_service',
                                                    'two_service']

        # check its signature is correct
        assert getattr(FunkyService.explicit_funky, '__di_name__') == \
            'FunkyService.explicit_funky'
        method_sig = getattr(FunkyService.explicit_funky, '__signature__')
        assert method_sig is not None
        assert list(method_sig.parameters.keys()) == ['self', 'one_service',
                                                      'two_service']

        # same for when the injectable parameters aren't explicitly set
        assert getattr(FunkyService.implicit_funky, '__di_name__') == \
            'FunkyService.implicit_funky'
        method_sig = getattr(FunkyService.implicit_funky, '__signature__')
        assert method_sig is not None
        assert list(method_sig.parameters.keys()) == ['self', 'one_service',
                                                      'two_service']

        assert getattr(WhyBoth, '__di_name__') == 'why_both'
        cls_sig = getattr(WhyBoth, '__signature__')
        init_sig = getattr(WhyBoth.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None

        with pytest.raises(ServiceUsageError) as e:
            unchained.services.pop('funky_service')
            WhyBoth()
        assert 'WhyBoth was initialized without the funky_service' in str(e)
