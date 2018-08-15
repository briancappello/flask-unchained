try:
    from flask_unchained.bundles.security import SecurityController
except ImportError:
    from flask_unchained import OptionalClass as SecurityController


class AdminSecurityController(SecurityController):
    template_folder = 'admin'
