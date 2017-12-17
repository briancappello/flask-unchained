from typing import List

from .bundle import Bundle


class Unchained:
    def __init__(self):
        self.app = None

        self._bundle_stores = {}
        self._registered_extensions = {}

    def init_app(self, app, bundles: List[Bundle]):
        self.app = app

        for bundle in bundles:
            if bundle.store is not None:
                self._bundle_stores[bundle.name] = bundle.store

        app.extensions['unchained'] = self

    def __getattr__(self, bundle_name):
        if bundle_name in self._bundle_stores:
            return self._bundle_stores[bundle_name]
        raise AttributeError(bundle_name)


unchained = Unchained()
