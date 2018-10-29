from flask import abort, current_app, request
from http import HTTPStatus

try:
    from flask_unchained.bundles.security import current_user as user
except ImportError:
    user = None

from flask_unchained import redirect, url_for


class AdminSecurityMixin:
    """
    Mixin class for Admin views providing integration with the Security Bundle.
    """

    def is_accessible(self):
        if (user.is_active
                and user.is_authenticated
                and user.has_role(current_app.config.ADMIN_ADMIN_ROLE_NAME)):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if not user.is_authenticated:
                return redirect(url_for('ADMIN_LOGIN_ENDPOINT', next=request.url))
            abort(HTTPStatus.FORBIDDEN)
