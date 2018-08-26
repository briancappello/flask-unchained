from flask_unchained import Bundle

from .extensions import Admin, admin
from .model_admin import ModelAdmin
from .macro import macro
from .security import AdminSecurityMixin
from .views import AdminDashboardView, AdminSecurityController


class AdminBundle(Bundle):
    """
    AdminBundle base class. Has no special behavior; subclass if you need to extend
    the admin bundle.
    """
    pass
