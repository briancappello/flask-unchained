try:
    from flask_security_bundle import SecurityController
except ImportError:
    from flask_unchained import OptionalClass as SecurityController


class AdminSecurityController(SecurityController):
    template_folder = 'admin'
