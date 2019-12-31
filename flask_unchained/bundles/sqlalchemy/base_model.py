from flask_sqlalchemy_unchained import BaseModel as _BaseModel, BaseQuery
from sqlalchemy.ext.declarative import declared_attr

from ...bundles.babel import lazy_gettext as _
from ...string_utils import pluralize, title_case
from .meta_options import ModelMetaOptionsFactory


class QueryAliasDescriptor:
    def __get__(self, instance, cls):
        return cls.query


class BaseModel(_BaseModel):
    """
    Base model class
    """
    _meta_options_factory_class = ModelMetaOptionsFactory
    gettext_fn = _

    query: BaseQuery
    q: BaseQuery = QueryAliasDescriptor()

    @declared_attr
    def __plural__(self):
        return pluralize(self.__name__)

    @declared_attr
    def __label__(self):
        return title_case(self.__name__)

    @declared_attr
    def __plural_label__(self):
        return title_case(pluralize(self.__name__))
