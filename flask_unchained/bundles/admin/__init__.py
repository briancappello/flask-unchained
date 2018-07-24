"""
    flask_unchained.bundles.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Integrates Flask Admin with Flask Unchained

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for details
"""

__version__ = '0.2.3'


from flask_unchained import Bundle

from .extensions import Admin
from .model_admin import ModelAdmin
from .macro import macro
from .security import AdminSecurityMixin
from .views import AdminDashboardView, AdminSecurityController


class AdminBundle(Bundle):
    pass
