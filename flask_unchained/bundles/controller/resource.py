from flask_unchained.string_utils import pluralize

from .controller import Controller
from .metaclasses import ResourceMeta
from .utils import controller_name


class UrlPrefixDescriptor:
    def __get__(self, instance, cls):
        return '/' + pluralize(controller_name(cls))


class Resource(Controller, metaclass=ResourceMeta):
    __abstract__ = True

    url_prefix = UrlPrefixDescriptor()
    member_param = '<int:id>'

    @classmethod
    def method_as_view(cls, method_name, *class_args, **class_kwargs):
        view = super().method_as_view(method_name, *class_args, **class_kwargs)
        view.methods = cls.resource_methods.get(method_name, None)
        return view
