import os
import sys


class Bundle:
    app_bundle = False
    """Whether or not this bundle is the top-level application bundle"""

    module_name = None  # type: str
    """Top-level module name of the bundle (dot notation)"""

    root_dir = None  # type: str
    """
    Top-level folder path of the bundle (defaults to the module's folder if
    not provided)
    """

    hooks = []

    def __init__(self):
        if not self.module_name:
            raise AttributeError(f'{self.__class__.__name__} is missing a '
                                 f'`module_name` attribute')

        if self.module_name.endswith('.bundle'):
            self.module_name = self.module_name[:-len('.bundle')]

        if not self.root_dir:
            self.root_dir = os.path.dirname(
                sys.modules[self.module_name].__file__)

    @property
    def name(self) -> str:
        if '.' not in self.module_name:
            return self.module_name
        return self.module_name.rsplit('.', maxsplit=1)[-1]
