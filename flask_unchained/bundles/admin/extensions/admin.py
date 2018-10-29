from flask import Flask
from flask_admin import Admin as BaseAdmin, helpers
from flask_unchained import url_for


class Admin(BaseAdmin):
    """
    The `Admin` extension::

        from flask_unchained.bundles.admin import admin
    """

    def init_app(self, app: Flask):
        self.app = app
        self.name = app.config.ADMIN_NAME
        self.subdomain = app.config.ADMIN_SUBDOMAIN
        self._set_admin_index_view(app.config.ADMIN_INDEX_VIEW,
                                   url=app.config.ADMIN_BASE_URL)
        self.base_template = app.config.ADMIN_BASE_TEMPLATE
        self.template_mode = app.config.ADMIN_TEMPLATE_MODE

        self._init_extension()

        # Register views
        for view in self._views:
            app.register_blueprint(view.create_blueprint(self),
                                   register_with_babel=False)

        app.context_processor(lambda: dict(admin_base_template=self.base_template,
                                           admin_view=self.index_view,
                                           h=helpers,
                                           get_url=url_for))

    def menu(self):
        return [item for item in super().menu() if item.name != 'Home']
