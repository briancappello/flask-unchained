from .utils import right_replace


class ModuleNameDescriptor:
    def __get__(self, instance, cls):
        return right_replace(cls.__module__, '.bundle', '')


class Bundle:
    app_bundle: bool = False
    """Whether or not this bundle is the top-level application bundle"""

    module_name: str = ModuleNameDescriptor()
    """Top-level module name of the bundle (dot notation)"""

    hooks = []

    store = None

    def __init__(self):
        # just in case the user explicitly set this attribute to a string
        if self.module_name.endswith('.bundle'):
            self.module_name = right_replace(self.module_name, '.bundle', '')

    @property
    def name(self) -> str:
        if '.' not in self.module_name:
            return self.module_name
        return self.module_name.rsplit('.', maxsplit=1)[-1]

    def __repr__(self):
        return f'<Bundle name={self.name!r} module={self.module_name!r}>'
