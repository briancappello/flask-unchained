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


@pytest.mark.bundles(['tests._bundles.services_ext_bundle'])
class TestInject:
    def test_services_named_correctly(self):
        from tests._bundles.services_ext_bundle.services import (
            OneService, TwoService, FunkyService, WhyBoth)

        assert getattr(OneService, '__di_name__') == 'one_service'
        assert getattr(TwoService, '__di_name__') == 'two_service'
        assert getattr(FunkyService, '__di_name__') == 'funky_service'
        assert getattr(WhyBoth, '__di_name__') == 'why_both'

    def test_services_keep_their_docstrings(self):
        from tests._bundles.services_ext_bundle.services import (
            OneService, TwoService, FunkyService, WhyBoth)

        assert 'ext one_service' in OneService.__doc__
        assert 'ext one_service __init__' in OneService.__init__.__doc__

        assert 'ext two_service' in TwoService.__doc__
        assert 'ext two_service __init__' in TwoService.__init__.__doc__

        assert 'ext funky_service' in FunkyService.__doc__
        assert 'ext funky_service __init__' in FunkyService.__init__.__doc__

        assert 'why_both' in WhyBoth.__doc__
        assert 'why_both __init__' in WhyBoth.__init__.__doc__

    def test_original_constructor_called(self):
        from tests._bundles.services_ext_bundle.services import OneService

        one_service = OneService()
        assert one_service.bundle == 'services_ext'

    def test_correct_signature_for_classes(self):
        from tests._bundles.services_ext_bundle.services import (
            OneService, BaseTwo, TwoService, FunkyService, WhyBoth)

        cls_sig = getattr(OneService, '__signature__')
        init_sig = getattr(OneService.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self']

        cls_sig = getattr(BaseTwo, '__signature__')
        init_sig = getattr(BaseTwo.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self', 'one_service']

        cls_sig = getattr(TwoService, '__signature__')
        init_sig = getattr(TwoService.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self', 'args', 'kwargs']

        cls_sig = getattr(FunkyService, '__signature__')
        init_sig = getattr(FunkyService.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self', 'one_service', 'two_service']

        cls_sig = getattr(WhyBoth, '__signature__')
        init_sig = getattr(WhyBoth.__init__, '__signature__')
        assert cls_sig == init_sig
        assert init_sig is not None
        assert list(init_sig.parameters.keys()) == ['self', 'funky_service']

    def test_correct_sig_for_wrapped_fn_with_explicit_args(self):
        from tests._bundles.services_ext_bundle.services import FunkyService

        assert getattr(FunkyService.explicit_funky, '__di_name__') == \
            'FunkyService.explicit_funky'
        method_sig = getattr(FunkyService.explicit_funky, '__signature__')
        assert method_sig is not None
        assert list(method_sig.parameters.keys()) == ['self', 'one_service',
                                                      'two_service']

    def test_correct_sig_for_wrapped_fn_without_explicit_args(self):
        from tests._bundles.services_ext_bundle.services import FunkyService

        assert getattr(FunkyService.implicit_funky, '__di_name__') == \
            'FunkyService.implicit_funky'
        method_sig = getattr(FunkyService.implicit_funky, '__signature__')
        assert method_sig is not None
        assert list(method_sig.parameters.keys()) == ['self', 'one_service',
                                                      'two_service']

    def test_service_initialized_without_dependency_injection(self):
        from tests._bundles.services_ext_bundle.services import (
            OneService, TwoService, WhyBoth)

        with pytest.raises(ServiceUsageError) as e:
            unchained.services.pop('one_service')
            TwoService()
        assert 'TwoService was initialized without the one_service' in str(e)

        one_service = OneService()
        two_service = TwoService(one_service)
        assert two_service.one_service.bundle == 'services_ext'

        with pytest.raises(ServiceUsageError) as e:
            unchained.services.pop('funky_service')
            WhyBoth()
        assert 'WhyBoth was initialized without the funky_service' in str(e)


class TestInjectedClassAttributes:
    @pytest.mark.bundles(['tests._bundles.services_bundle'])
    def test_injected_class_attrs(self):
        from tests._bundles.services_bundle.services import OneService, TwoService
        assert isinstance(unchained.services.class_attr_service.one_service, OneService)
        assert isinstance(unchained.services.class_attr_service.two_service, TwoService)

    @pytest.mark.bundles(['tests._bundles.services_bundle'])
    def test_injected_class_attrs_on_extended_service(self):
        from tests._bundles.services_bundle.services import (
            OneService, TwoService, FunkyService)
        assert isinstance(unchained.services.extended_class_attr_service.one_service,
                          OneService)
        assert isinstance(unchained.services.extended_class_attr_service.two_service,
                          TwoService)
        assert isinstance(unchained.services.extended_class_attr_service.funky_service,
                          FunkyService)

    @pytest.mark.bundles(['tests._bundles.services_ext_bundle'])
    def test_injected_class_attrs_on_extended_service_with_same_name_as_base(self):
        from tests._bundles.services_ext_bundle.services import (
            OneService, TwoService, FunkyService)
        assert isinstance(unchained.services.class_attr_service.one_service, OneService)
        assert isinstance(unchained.services.class_attr_service.two_service, TwoService)
        assert isinstance(unchained.services.class_attr_service.funky_service,
                          FunkyService)

    @pytest.mark.bundles(['tests._bundles.services_bundle'])
    def test_injected_class_attrs_with_init(self):
        from tests._bundles.services_bundle.services import (
            OneService, TwoService, FunkyService)
        assert isinstance(unchained.services.class_attr_service_with_init.one_service,
                          OneService)
        assert isinstance(unchained.services.class_attr_service_with_init.two_service,
                          TwoService)
        assert isinstance(unchained.services.class_attr_service_with_init.funky_service,
                          FunkyService)

    @pytest.mark.bundles(['tests._bundles.services_bundle'])
    def test_injected_class_attrs_extended_and_with_init(self):
        from tests._bundles.services_bundle.services import (
            OneService, TwoService, ThreeService, FourService, FunkyService)
        assert isinstance(unchained.services.extended_class_attr_with_init.one_service,
                          OneService)
        assert isinstance(unchained.services.extended_class_attr_with_init.two_service,
                          TwoService)
        assert isinstance(unchained.services.extended_class_attr_with_init.three_service,
                          ThreeService)
        assert isinstance(unchained.services.extended_class_attr_with_init.four_service,
                          FourService)
        assert isinstance(unchained.services.extended_class_attr_with_init.funky_service,
                          FunkyService)
