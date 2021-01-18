from flask_admin import Admin as BaseAdmin
from flask_unchained import FlaskUnchained


class Admin(BaseAdmin):
    """
    The `Admin` extension::

        from flask_unchained.bundles.admin import admin
    """

    def init_app(self, app: FlaskUnchained):
        self.app = app
        self.name = app.config.ADMIN_NAME
        self.subdomain = app.config.ADMIN_SUBDOMAIN
        self.base_template = app.config.ADMIN_BASE_TEMPLATE
        self.template_mode = app.config.ADMIN_TEMPLATE_MODE

        # NOTE: AdminBundle.after_init_app finishes initializing this extension
        # (unfortunately the admin extension is deeply integrated with its own blueprints,
        #  so this delayed initialization is necessary for template overriding to work)
