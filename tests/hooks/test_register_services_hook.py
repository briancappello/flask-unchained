import pytest

from flask_unchained import unchained


class TestRegisterServicesHook:
    @pytest.mark.bundles(['tests._bundles.services_bundle'])
    def test_services_get_detected_and_initialized(self):
        from tests._bundles.services_bundle.services import (
            OneService, TwoService, FunkyService)
        assert isinstance(unchained.services.one_service, OneService)
        assert isinstance(unchained.services.two_service, TwoService)
        assert isinstance(unchained.services.funky_service, FunkyService)

    @pytest.mark.bundles(['tests._bundles.services_ext_bundle'])
    def test_bundle_overriding_services_works(self, app):
        from tests._bundles.services_ext_bundle.services import (
            OneService, TwoService, FunkyService)
        assert isinstance(unchained.services.one_service, OneService)
        assert isinstance(unchained.services.two_service, TwoService)
        assert isinstance(unchained.services.funky_service, FunkyService)
