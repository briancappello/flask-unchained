from flask_admin import helpers
from flask_unchained import Bundle, FlaskUnchained, url_for

from .extensions import Admin, admin
from .model_admin import ModelAdmin
from .macro import macro
from .security import AdminSecurityMixin
from .views import AdminDashboardView, AdminSecurityController


class AdminBundle(Bundle):
    """
    The Admin Bundle.
    """

    name = 'admin_bundle'
    """
    The name of the Admin Bundle.
    """

    def after_init_app(self, app: FlaskUnchained) -> None:
        admin._set_admin_index_view(app.config.ADMIN_INDEX_VIEW,
                                    url=app.config.ADMIN_BASE_URL)
        admin._init_extension()

        # Register views
        for view in admin._views:
            app.register_blueprint(view.create_blueprint(admin),
                                   register_with_babel=False)

        app.context_processor(lambda: dict(admin_base_template=admin.base_template,
                                           admin_view=admin.index_view,
                                           h=helpers,
                                           get_url=url_for))
