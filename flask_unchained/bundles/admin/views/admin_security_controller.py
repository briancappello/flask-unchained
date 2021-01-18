from http import HTTPStatus

from flask_unchained import request, route, lazy_gettext as _

try:
    from flask_unchained.bundles.security import SecurityController, current_user
except ImportError:
    from py_meta_utils import OptionalClass as SecurityController


class AdminSecurityController(SecurityController):
    """
    Extends :class:`~flask_unchained.bundles.security.SecurityController`, to
    customize the template folder to use admin-specific templates.
    """
    class Meta:
        template_folder = 'admin'

    @route(endpoint='admin.logout')
    def logout(self):
        """
        View function to log a user out. Supports html and json requests.
        """
        if current_user.is_authenticated:
            self.security_service.logout_user()

        if request.is_json:
            return '', HTTPStatus.NO_CONTENT

        self.flash(_('flask_unchained.bundles.security:flash.logout'),
                   category='success')
        return self.redirect('ADMIN_POST_LOGOUT_REDIRECT_ENDPOINT',
                             'SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT')
