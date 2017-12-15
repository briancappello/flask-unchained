

class Bundle:
    app_bundle = False
    """Whether or not this bundle is the top-level application bundle"""

    module_name = None  # type: str
    """Top-level module name of the bundle (dot notation)"""

    hooks = []

    def __init__(self):
        if not self.module_name:
            raise AttributeError(f'{self.__class__.__name__} is missing a '
                                 f'`module_name` attribute')

        if self.module_name.endswith('.bundle'):
            self.module_name = self.module_name[:-len('.bundle')]

    @property
    def name(self) -> str:
        if '.' not in self.module_name:
            return self.module_name
        return self.module_name.rsplit('.', maxsplit=1)[-1]

    def __repr__(self):
        return f'<Bundle name={self.name!r} module={self.module_name!r}>'
