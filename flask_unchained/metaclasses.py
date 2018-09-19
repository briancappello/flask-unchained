import os

from collections import namedtuple

from .constants import TEST
from .utils import _missing


McsInitArgs = namedtuple('McsInitArgs', ('cls', 'name', 'bases', 'clsdict'))


class McsArgs:
    def __init__(self, mcs, name, bases, clsdict):
        self.mcs = mcs
        self.name = name
        self.bases = bases
        self.clsdict = clsdict

    @property
    def module(self):
        return self.clsdict.get('__module__')

    @property
    def model_repr(self):
        if self.module:
            return f'{self.module}.{self.name}'
        return self.name

    @property
    def model_meta(self):
        return self.clsdict['_meta']

    def __iter__(self):
        return iter([self.mcs, self.name, self.bases, self.clsdict])

    def __repr__(self):
        return f'<McsArgs model={self.model_repr}>'


class MetaOption:
    def __init__(self, name, default=None, inherit=False):
        self.name = name
        self.default = default
        self.inherit = inherit

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        """
        :param meta: the class Meta (if any) from the user's model (NOTE:
            this will be a plain object, NOT an instance of ModelMetaOptions)
        :param base_model_meta: the ModelMetaOptions (if any) from the
            base class of the user's model
        :param mcs_args: the McsArgs for the user's model class
        """
        value = self.default
        if self.inherit and base_model_meta is not None:
            value = getattr(base_model_meta, self.name, value)
        if meta is not None:
            value = getattr(meta, self.name, value)
        return value

    def check_value(self, value, mcs_args: McsArgs):
        pass

    def contribute_to_class(self, mcs_args: McsArgs, value):
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name!r}, ' \
               f'default={self.default!r}, inherit={self.inherit}>'


class AbstractMetaOption(MetaOption):
    def __init__(self):
        super().__init__(name='abstract', default=False, inherit=False)

    def get_value(self, meta, base_model_meta, mcs_args: McsArgs):
        if '__abstract__' in mcs_args.clsdict:
            return True
        return super().get_value(meta, base_model_meta, mcs_args)

    def contribute_to_class(self, mcs_args: McsArgs, is_abstract):
        if is_abstract:
            mcs_args.clsdict['__abstract__'] = True


class MetaOptionsFactory:
    options = []

    def __init__(self):
        self._mcs_args: McsArgs = None

    def _get_meta_options(self):
        return [option if isinstance(option, MetaOption) else option()
                for option in self.options]

    def _contribute_to_class(self, mcs_args: McsArgs):
        self._mcs_args = mcs_args

        meta = mcs_args.clsdict.pop('Meta', None)
        base_model_meta = deep_getattr(
            mcs_args.clsdict, mcs_args.bases, '_meta', None)

        mcs_args.clsdict['_meta'] = self

        options = self._get_meta_options()
        if (any(isinstance(mo, AbstractMetaOption) for mo in self._get_meta_options())
                and os.getenv('FLASK_ENV', None) != TEST
                and not isinstance(options[0], AbstractMetaOption)):
            raise Exception('The first option returned by _get_meta_options '
                            'must be an instance of AbstractMetaOption')

        self._fill_from_meta(meta, base_model_meta, mcs_args)
        for option in options:
            option_value = getattr(self, option.name, None)
            option.contribute_to_class(mcs_args, option_value)

    def _fill_from_meta(self, meta, base_model_meta, mcs_args: McsArgs):
        # Exclude private/protected fields from the meta
        meta_attrs = {} if not meta else {k: v for k, v in vars(meta).items()
                                          if not k.startswith('_')}

        for option in self._get_meta_options():
            assert not hasattr(self, option.name), \
                f"Can't override field {option.name}."
            value = option.get_value(meta, base_model_meta, mcs_args)
            option.check_value(value, mcs_args)
            meta_attrs.pop(option.name, None)
            if option.name != '_':
                setattr(self, option.name, value)

        if meta_attrs:
            # Some attributes in the Meta aren't allowed here
            raise TypeError(
                f"'class Meta' for {self._mcs_args.name!r} got unknown "
                f"attribute(s) {','.join(sorted(meta_attrs.keys()))}")

    def __repr__(self):
        return '<{cls} meta_options={attrs!r}>'.format(
            cls=self.__class__.__name__,
            attrs={option.name: getattr(self, option.name, None)
                   for option in self._get_meta_options()})


def deep_getattr(clsdict, bases, name, default=_missing):
    """
    Acts just like getattr would on a constructed class object, except this operates
    on the pre-class-construction class dictionary and base classes. In other words,
    first we look for the attribute in the class dictionary, and then we search all the
    base classes (in method resolution order), finally returning the default value if
    the attribute was not found in any of the class dictionary or base classes.
    """
    value = clsdict.get(name, _missing)
    if value != _missing:
        return value
    for base in bases:
        value = getattr(base, name, _missing)
        if value != _missing:
            return value
    if default != _missing:
        return default
    raise AttributeError(name)
