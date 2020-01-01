from flask_unchained import Bundle

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
