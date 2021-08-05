from flask_unchained import url_for
from markupsafe import Markup as safe
from sqlalchemy.ext.associationproxy import _AssociationCollection
from sqlalchemy_unchained.utils import rec_getattr
from typing import *


def admin_link(
    admin_controller: str,
    *,
    view: str,
    label: Union[str, Optional[Callable[[object], str]]] = None,
    tooltip: Union[str, Optional[Callable[[object, str], str]]] = None,
    multiline_many: bool = False,
):
    ctrl = (admin_controller
            if '_admin' in admin_controller
            else f'{admin_controller}_admin')

    def column_formatter(admin_view, ctx, model_instance, column):
        def get_label(obj):
            if callable(label):
                return label(obj)
            return rec_getattr(obj, label or column)

        def get_title(obj, text):
            if callable(tooltip):
                return tooltip(obj, text)
            return tooltip

        def a_tag(obj):
            href = url_for(f'{ctrl}.{view}', id=getattr(obj, obj.Meta.pk))
            text = get_label(obj)
            title = get_title(obj, text)
            return f'<a href="{href}" title="{title or ""}">{text}</a>'

        column_value = rec_getattr(model_instance, column)
        if not isinstance(column_value, (list, tuple, _AssociationCollection)):
            return safe(a_tag(model_instance))

        a_tags = [a_tag(obj) for obj in column_value]
        if not multiline_many:
            return safe(', '.join(a_tags))
        return safe(''.join(f'<p>{tag}</p>' for tag in a_tags))

    return column_formatter


def create_link(
    admin_controller: str,
    *,
    label: Union[str, Optional[Callable[[object], str]]] = None,
    tooltip: Union[str, Optional[Callable[[object, str], str]]] = None,
    multiline_many: bool = False,
):
    return admin_link(admin_controller,
                      view='create_view',
                      label=label,
                      tooltip=tooltip,
                      multiline_many=multiline_many)


def edit_link(
    admin_controller: str,
    *,
    label: Union[str, Optional[Callable[[object], str]]] = None,
    tooltip: Union[str, Optional[Callable[[object, str], str]]] = None,
    multiline_many: bool = False,
):
    return admin_link(admin_controller,
                      view='edit_view',
                      label=label,
                      tooltip=tooltip or (lambda obj, text: f'Edit {text}'),
                      multiline_many=multiline_many)


def delete_link(
    admin_controller: str,
    *,
    label: Union[str, Optional[Callable[[object], str]]] = None,
    tooltip: Union[str, Optional[Callable[[object, str], str]]] = None,
    multiline_many: bool = False,
):
    return admin_link(admin_controller,
                      view='delete_view',
                      label=label,
                      tooltip=tooltip or (lambda obj, text: f'Delete {text}'),
                      multiline_many=multiline_many)


def details_link(
    admin_controller: str,
    *,
    label: Union[str, Optional[Callable[[object], str]]] = None,
    tooltip: Union[str, Optional[Callable[[object, str], str]]] = None,
    multiline_many: bool = False,
):
    return admin_link(admin_controller,
                      view='details_view',
                      label=label,
                      tooltip=tooltip or (lambda obj, text: f'View {text} details'),
                      multiline_many=multiline_many)


def index_link(
    admin_controller: str,
    *,
    label: Union[str, Optional[Callable[[object], str]]] = None,
    tooltip: Union[str, Optional[Callable[[object, str], str]]] = None,
    multiline_many: bool = False,
):
    return admin_link(admin_controller,
                      view='index_view',
                      label=label,
                      tooltip=tooltip,
                      multiline_many=multiline_many)
