from datetime import date, datetime

from flask_admin.contrib.sqla import ModelView as _BaseModelAdmin
from flask_admin.consts import ICON_TYPE_GLYPH
from flask_unchained.string_utils import slugify, snake_case

from .forms import ReorderableForm, AdminModelFormConverter
from .macro import macro
from .security import AdminSecurityMixin


EXTEND_BASE_CLASS_ATTRIBUTES = (
    'column_formatters',
    'column_type_formatters',
)


class _ModelAdminNameDescriptor:
    def __get__(self, instance, cls):
        if not cls.model or isinstance(cls.model, str):
            return None
        return cls.model.__plural_label__


class _ModelAdminEndpointDescriptor:
    def __get__(self, instance, cls):
        return snake_case(cls.__name__)


class _ModelAdminSlugDescriptor:
    def __get__(self, instance, cls):
        if not cls.model or isinstance(cls.model, str):
            return None
        return slugify(cls.model.__plural_label__)


class ModelAdmin(AdminSecurityMixin, _BaseModelAdmin):
    """
    Base class for SQLAlchemy model admins. More or less the same as
    :class:`~flask_admin.contrib.sqla.ModelView`, except we set some
    different defaults.
    """

    can_view_details = True

    name = _ModelAdminNameDescriptor()
    endpoint = _ModelAdminEndpointDescriptor()
    slug = _ModelAdminSlugDescriptor()

    model = None
    category_name = None
    menu_class_name = None
    menu_icon_type = ICON_TYPE_GLYPH
    menu_icon_value = None

    column_exclude_list = ('created_at', 'updated_at')
    form_excluded_columns = ('created_at', 'updated_at')

    column_type_formatters = {
        datetime: lambda view, dt: dt.strftime('%-m/%-d/%Y %-I:%M %p %Z'),
        date: lambda view, d: d.strftime('%-m/%-d/%Y'),
    }

    column_formatters = {
        'created_at': macro('column_formatters.datetime'),
        'updated_at': macro('column_formatters.datetime'),
    }

    form_base_class = ReorderableForm
    model_form_converter = AdminModelFormConverter

    def __getattribute__(self, item):
        """Allow class attribute names in EXTEND_BASE_CLASS_ATTRIBUTES that are
        defined on subclasses to automatically extend the equivalently named
        attribute on this base class

        (a bit of an ugly hack, but hey, it's only the admin)
        """
        value = super().__getattribute__(item)
        if item in EXTEND_BASE_CLASS_ATTRIBUTES and value is not None:
            base_value = getattr(ModelAdmin, item)
            base_value.update(value)
            return base_value
        return value
