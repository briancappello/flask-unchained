from datetime import date, datetime

from flask_admin.base import AdminViewMeta as _AdminViewMeta
from flask_admin.contrib.sqla import ModelView as _BaseModelAdmin
from flask_admin.consts import ICON_TYPE_FONT_AWESOME
from flask_admin.model import typefmt
from sqlalchemy.ext.associationproxy import _AssociationList

from flask_unchained.di import _set_up_class_dependency_injection
from flask_unchained.string_utils import slugify, snake_case
from py_meta_utils import McsArgs

from .forms import ReorderableForm, AdminModelFormConverter
from .macro import macro
from .security import AdminSecurityMixin


EXTEND_BASE_CLASS_DICT_ATTRIBUTES = (
    "column_formatters",
    "column_formatters_detail",
    "column_type_formatters",
    "column_type_formatters_detail",
)
EXTEND_BASE_CLASS_LIST_ATTRIBUTES = (
    "column_exclude_list",
    "form_excluded_columns",
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


class ModelAdminMetaclass(_AdminViewMeta):
    def __new__(mcs, name, bases, clsdict):
        mcs_args = McsArgs(mcs, name, bases, clsdict)
        _set_up_class_dependency_injection(mcs_args)
        return super().__new__(*mcs_args)


class ModelAdmin(AdminSecurityMixin, _BaseModelAdmin, metaclass=ModelAdminMetaclass):
    """
    Base class for SQLAlchemy model admins. More or less the same as
    :class:`~flask_admin.contrib.sqla.ModelView`, except we set some
    improved defaults. A brief summary of attributes you can set on
    subclasses is shown below:

    .. code-block::

        # ALL VIEWS
        # ---------
        model = ModelClass
        column_labels = dict(model_attr_name='Label')
        column_descriptions = dict(model_attr_name='Description (tooltip help text)')

        # LIST
        # ----
        list_template = 'admin/model/list.html'
        column_list = ('columns', 'to', 'show', 'in', 'list', 'view')
        column_default_sort = 'default_column_to_sort_on'
        column_sortable_list = ('sortable', 'column', 'headers')
        column_exclude_list = ('columns', 'to', 'exclude')
        column_editable_list = ('columns', 'to', 'inline', 'edit', 'in', 'list', 'view')
        column_filters = ('filterable', 'columns')  # column names or instances of BaseFilter classes
        column_searchable_list = ('searchable', 'columns')
        column_choices = {
            'column_name': [
                ('db_value', 'display_value'),
            ],
        }
        column_formatters = dict(
            attr_name=lambda view, context, model, attr_name: getattr(model, attr_name),
            attr_name=macro('macro_name'),
        )
        column_type_formatters = dict(
            type=lambda view, value: repr(value),
        )

        action_disallowed_list = ('disallowed', 'action', 'names')
        column_display_actions: bool = True  # show/hide the Actions column of links in the list view
        column_extra_row_actions = [BaseListRowActionSubclass('fa fa-whatever', 'my_view.endpoint')]

        page_size = 20  # default pagination size
        can_set_page_size: bool = False  # show a dropdown for setting pagination size

        # CREATE
        # ------
        can_create: bool = True  # allow creation
        create_modal: bool = False   # setting to True makes the create form a modal dialog
        create_template = 'admin/model/create.html'
        form_create_rules = 'https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.form_create_rules'

        # EDIT
        # ----
        can_edit: bool = True  # allow editing
        edit_modal: bool = False  # setting to True shows edit form as a modal
        edit_modal_template = 'admin/model/modals/edit.html'
        edit_template = 'admin/model/edit.html'
        form_edit_rules = 'https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.form_edit_rules'

        # CREATE & EDIT
        # -------------
        form = CustomFormClass  # completely disables automatic form scaffolding functionality
        form_base_class = CustomFormBaseClass  # uses automatic form scaffolding functionality
        form_columns = ('columns', 'to', 'include', 'in', 'form')  # also controls order
        form_excluded_columns = ('columns', 'to', 'exclude', 'from', 'form')
        form_args = {  # kwargs to pass into WTForms Field classes
            'column_name': dict(label='Column Name', validators=[]),
        }
        form_overrides = {
            'column_name': wtforms.fields.FieldClass,
        }
        form_widget_args = {
            'column_name': dict(form_widget_kwarg=value),
        }
        form_extra_fields = dict(additional_field_name=wtforms.fields.FieldClass('Label'))
        form_ajax_refs = dict(field_name=dict(kwargs_to_ajax_model_loader))
        form_rules = https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.form_rules

        # DETAILS
        # -------
        can_view_details: bool = True  # show details tab
        details_modal: bool = False  # setting to True shows details as a modal
        details_modal_template = 'admin/model/modals/details.html'
        details_template = 'admin/model/details.html'
        column_details_list = ('columns', 'to', 'show')
        column_details_exclude_list = ('columns', 'to', 'exclude')
        column_formatters_detail = dict(  # same as column_formatters, however, macros aren't supported(!?)
            column_name=lambda view, context, model, attr_name: getattr(model, attr_name),
        )
        column_type_formatters_detail = dict(type=lambda view, value: repr(value))

        # DELETE
        # ------
        can_delete: bool = True  # allow deletion

        # EXPORT
        # ------
        can_export: bool = False  # allow exporting data from the list view
        column_export_list = ('list', 'of', 'columns', 'to', 'export')
        column_export_exclude_list = ('list', 'of', 'columns', 'to', 'exclude')
        column_formatters_export = dict(  # same as column_formatters, however, macros aren't supported(!?)
            column_name=lambda view, context, model, attr_name: getattr(model, attr_name),
        )
        column_type_formatters_export = dict(type=lambda view, value: repr(value))
        export_max_rows = 0  # 0==unlimited (default), None==self.page_size, N=limit
        export_types = ('csv',)  # any format supported by https://github.com/kennethreitz/tablib/

    """

    can_view_details = True
    named_filter_urls = True

    name = _ModelAdminNameDescriptor()
    endpoint = _ModelAdminEndpointDescriptor()
    slug = _ModelAdminSlugDescriptor()

    model = None
    category_name = None
    menu_class_name = None
    menu_icon_type = ICON_TYPE_FONT_AWESOME
    menu_icon_value = None

    column_exclude_list = ("created_at", "updated_at")
    form_excluded_columns = ("created_at", "updated_at")

    column_formatters = {
        "created_at": macro("column_formatters.datetime"),
        "updated_at": macro("column_formatters.datetime"),
    }

    column_type_formatters = {
        datetime: lambda view, dt: dt.strftime("%Y-%m-%d %I:%M%p %Z"),
        date: lambda view, d: d.strftime("%Y-%m-%d"),
        _AssociationList: lambda view, values: ", ".join(str(v) for v in values),
        **typefmt.BASE_FORMATTERS,
    }

    form_base_class = ReorderableForm
    model_form_converter = AdminModelFormConverter

    def _refresh_cache(self):
        super()._refresh_cache()

        # details view should inherit formatters from the list view
        self.column_formatters_detail = {
            **self.column_formatters_detail,
            **{
                k: v
                for k, v in self.column_formatters.items()
                if k not in self.column_formatters_detail
            },
        }

        # details view should inherit formatters from the list view
        self.column_type_formatters_detail = {
            **self.column_type_formatters_detail,
            **{
                k: v
                for k, v in self.column_type_formatters.items()
                if k not in self.column_type_formatters_detail
            },
        }

    def __getattribute__(self, attr):
        """Allow class attribute names in EXTEND_BASE_CLASS_DICT_ATTRIBUTES
        that are defined on subclasses to automatically extend the equivalently
        named attribute on this base class.

        (a bit of an ugly hack, but hey, it's only the admin)
        """
        value = super().__getattribute__(attr)
        if attr in EXTEND_BASE_CLASS_DICT_ATTRIBUTES and isinstance(value, dict):
            base_value = (getattr(ModelAdmin, attr) or {}).copy()
            if isinstance(base_value, dict):
                base_value.update(value)
                return base_value
        elif attr in EXTEND_BASE_CLASS_LIST_ATTRIBUTES and isinstance(
            value, (list, tuple)
        ):
            base_value = getattr(ModelAdmin, attr)
            if isinstance(base_value, (list, tuple)):
                return tuple(list(value) + [v for v in base_value if v not in value])
        return value
