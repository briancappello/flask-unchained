import re

from collections import defaultdict
from flask_sqlalchemy.model import DefaultMeta, should_set_tablename
from flask_unchained.string_utils import snake_case
from flask_unchained.utils import deep_getattr
from sqlalchemy import Column

from .model_meta_factory import ModelMetaFactory
from .model_registry import _model_registry
from .types import McsArgs, McsInitArgs

VALIDATOR_RE = re.compile(r'^validates?_(?P<column>\w+)')


class BaseModelMetaclass(DefaultMeta):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        _model_registry._ensure_correct_base_model(mcs_args)

        ModelMetaFactoryClass = deep_getattr(
            clsdict, mcs_args.bases, '_meta_factory_class', ModelMetaFactory)
        model_meta_factory: ModelMetaFactory = ModelMetaFactoryClass()
        model_meta_factory._contribute_to_class(mcs_args)

        if model_meta_factory.abstract:
            return super().__new__(*mcs_args)

        validators = deep_getattr(clsdict, mcs_args.bases, '__validators__',
                                  defaultdict(list))
        columns = {col_name: col for col_name, col in clsdict.items()
                   if isinstance(col, Column)}
        for col_name, col in columns.items():
            if not col.name:
                col.name = col_name
            if col.info:
                for v in col.info.get('validators', []):
                    if v not in validators[col_name]:
                        validators[col_name].append(v)

        for attr_name, attr in clsdict.items():
            validates = getattr(attr, '__validates__', None)
            if validates and deep_getattr(clsdict, mcs_args.bases, validates):
                if attr_name not in validators[attr.__validates__]:
                    validators[attr.__validates__].append(attr_name)
                continue

            m = VALIDATOR_RE.match(attr_name)
            column = m.groupdict()['column'] if m else None
            if m and deep_getattr(clsdict, mcs_args.bases, column, None) is not None:
                attr.__validates__ = column
                if attr_name not in validators[column]:
                    validators[column].append(attr_name)
        clsdict['__validators__'] = validators

        _model_registry.register_new(mcs_args)
        return super().__new__(*mcs_args)

    def __init__(cls, name, bases, clsdict):
        # for some as-yet-not-understood reason, the arguments python passes
        # to __init__ do not match those we gave to __new__ (namely, the
        # bases parameter passed to __init__ is what the class was declared
        # with, instead of the new bases the model_registry determined it
        # should have. and in fact, __new__ does the right thing - it uses
        # the correct bases, and the generated class has the correct bases,
        # yet still, the ones passed to __init__ are wrong. however at this
        # point (inside __init__), because the class has already been
        # constructed, changing the bases argument doesn't seem to have any
        # effect (and that agrees with what conceptually should be the case).
        # Sooo, we're passing the correct arguments up the chain, to reduce
        # confusion, just in case anybody needs to inspect them)
        _, name, bases, clsdict = cls._meta._mcs_args

        if cls._meta.abstract:
            super().__init__(name, bases, clsdict)

        if should_set_tablename(cls):
            cls.__tablename__ = snake_case(cls.__name__)

        if not cls._meta.abstract and not cls._meta.lazy_mapped:
            cls._pre_mcs_init()
            super().__init__(name, bases, clsdict)
            cls._post_mcs_init()

        if not cls._meta.abstract:
            _model_registry.register(McsInitArgs(cls, name, bases, clsdict))

    def _pre_mcs_init(cls):
        """
        Callback for BaseModelMetaclass subclasses to run code just before a
        concrete Model class gets registered with SQLAlchemy.

        This is intended to be used for advanced meta options implementations.
        """
        # technically you could also put a @classmethod with the same name on
        # the Model class, if you prefer that approach

    def _post_mcs_init(cls):
        """
        Callback for BaseModelMetaclass subclasses to run code just after a
        concrete Model class gets registered with SQLAlchemy.

        This is intended to be used for advanced meta options implementations.
        """
