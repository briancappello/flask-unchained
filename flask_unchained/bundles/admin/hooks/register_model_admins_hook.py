from flask_unchained import AppFactoryHook

from ..model_admin import ModelAdmin


class RegisterModelAdminsHook(AppFactoryHook):
    """
    Registers ModelAdmins.
    """

    bundle_module_name = 'admins'
    name = 'admins'
    run_after = ['bundle_template_folders', 'extensions', 'models']
    run_before = ['init_extensions']

    def process_objects(self, app, objects):
        admin = self.unchained.extensions.admin
        admin.category_icon_classes = app.config.ADMIN_CATEGORY_ICON_CLASSES

        db = self.unchained.extensions.db
        models = self.unchained.sqlalchemy_bundle.models

        for admin_name, admin_cls in objects.items():
            model = (admin_cls.model if not isinstance(admin_cls.model, str)
                     else models[admin_cls.model])
            admin_cls.model = model

            model_admin = admin_cls(
                model=admin_cls.model,
                session=db.session,
                name=admin_cls.name,
                endpoint=admin_cls.endpoint,
                url=app.config.ADMIN_BASE_URL + '/' + admin_cls.slug,
                category=admin_cls.category_name,
                menu_class_name=admin_cls.menu_class_name,
                menu_icon_value=admin_cls.menu_icon_value,
                menu_icon_type=(None if not admin_cls.menu_icon_value
                                else admin_cls.menu_icon_type))

            admin.add_view(model_admin)

    def type_check(self, obj):
        is_class = isinstance(obj, type) and issubclass(obj, ModelAdmin)
        return is_class and obj != ModelAdmin
