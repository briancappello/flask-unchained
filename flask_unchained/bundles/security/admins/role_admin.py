from flask_unchained.bundles.admin import ModelAdmin
from flask_unchained.bundles.admin.templates import details_link, edit_link

from ..models import Role


class RoleAdmin(ModelAdmin):
    model = Role

    name = "Roles"
    category_name = "Security"
    menu_icon_value = "fa fa-key"

    column_searchable_list = ("name",)
    column_sortable_list = ("name",)

    column_formatters = dict(name=details_link("role"))
    column_formatters_detail = dict(name=edit_link("role"))

    form_columns = ("name",)

    column_details_list = ("id", "name", "created_at", "updated_at")
