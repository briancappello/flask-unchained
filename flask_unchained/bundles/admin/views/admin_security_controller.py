try:
    from flask_unchained.bundles.security import SecurityController
except ImportError:
    from flask_unchained import OptionalClass as SecurityController


class AdminSecurityController(SecurityController):
    """
    Extends :class:`~flask_unchained.bundles.security.SecurityController`, to
    customize the template folder to use admin-specific templates.
    """

    template_folder = 'admin'
