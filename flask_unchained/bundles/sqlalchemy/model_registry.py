import sys

from sqlalchemy_unchained import ModelRegistry


class UnchainedModelRegistry(ModelRegistry):
    enable_lazy_mapping = True

    def _reset(self):
        for model in self._registry:
            for model_module in self._registry[model]:
                try:
                    del sys.modules[model_module]
                except KeyError:
                    pass

        super()._reset()


ModelRegistry.set_singleton_class(UnchainedModelRegistry)
