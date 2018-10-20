try:
    from flask_unchained.bundles.security import SecurityController
except ImportError:
    from py_meta_utils import OptionalClass as SecurityController


class AdminSecurityController(SecurityController):
    """
    Extends :class:`~flask_unchained.bundles.security.SecurityController`, to
    customize the template folder to use admin-specific templates.
    """
    class Meta:
        template_folder_name = 'admin'
