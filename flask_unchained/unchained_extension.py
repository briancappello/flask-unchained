from typing import List

from .bundle import Bundle


class _UnchainedState:
    def __init__(self):
        self._bundle_stores = {}
        self._extensions = {}

    def __getattr__(self, name):
        if name in self._bundle_stores:
            return self._bundle_stores[name]
        elif name in self._extensions:
            return self._extensions[name]
        raise AttributeError(name)


class Unchained:
    def __init__(self):
        pass

    def init_app(self, app, bundles: List[Bundle]):
        state = _UnchainedState()

        for bundle in bundles:
            if bundle.store is not None:
                state._bundle_stores[bundle.name] = bundle.store

        app.extensions['unchained'] = state
