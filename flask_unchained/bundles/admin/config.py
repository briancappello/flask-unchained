from flask_unchained import BundleConfig

from .views import AdminDashboardView


class Config(BundleConfig):
    """
    Config class for the Admin bundle. Defines which configuration values
    this bundle supports, and their default values.
    """

    ADMIN_NAME = 'Admin'
    """
    The title of the admin section of the site.
    """

    ADMIN_BASE_URL = '/admin'
    """
    Base url of the admin section of the site.
    """

    ADMIN_INDEX_VIEW = AdminDashboardView()
    """
    The :class:`~flask_admin.AdminIndexView` (or subclass) instance to use
    for the index view.
    """

    ADMIN_SUBDOMAIN = None
    """
    Subdomain of the admin section of the site.
    """

    ADMIN_BASE_TEMPLATE = 'admin/base.html'
    """
    Base template to use for other admin templates.
    """

    ADMIN_TEMPLATE_MODE = 'bootstrap3'
    """
    Which version of bootstrap to use. (bootstrap2 or bootstrap3)
    """

    ADMIN_CATEGORY_ICON_CLASSES = {}
    """
    Dictionary of admin category icon classes. Keys are category names,
    and the values depend on which version of bootstrap you're using.

    For example, with bootstrap3::

        ADMIN_CATEGORY_ICON_CLASSES = {
            'Mail': 'glyphicon glyphicon-envelope',
            'Security': 'glyphicon glyphicon-lock',
        }
    """

    ADMIN_ADMIN_ROLE_NAME = 'ROLE_ADMIN'
    """
    The name of the Role which represents an admin.
    """

    ADMIN_LOGIN_ENDPOINT = 'security.login'
    """
    Name of the endpoint to use for the admin login view.
    """

    ADMIN_LOGOUT_ENDPOINT = 'security.logout'
    """
    Name of the endpoint to use for the admin logout view.
    """

    ADMIN_POST_LOGOUT_ENDPOINT = '/'
    """
    Endpoint to redirect to after the user logs out of the admin.
    """
