"""
    Admin Bundle
    ------------

    Integrates Flask Admin with Flask Unchained

    Dependencies:

    * flask-admin >= 1.5

    .. automodule:: flask_unchained.bundles.admin.config
       :members:

"""

from flask_unchained import Bundle

from .extensions import Admin
from .model_admin import ModelAdmin
from .macro import macro
from .security import AdminSecurityMixin
from .views import AdminDashboardView, AdminSecurityController


class AdminBundle(Bundle):
    """
    AdminBundle base class. Subclass if you need to extend or customize
    anything in this bundle.
    """
    pass
