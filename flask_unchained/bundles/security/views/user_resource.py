from flask_unchained import injectable
from flask_unchained.bundles.api import ModelResource
from flask_unchained.bundles.controller.constants import CREATE, GET, PATCH

from ..decorators import anonymous_user_required, auth_required_same_user
from ..models import User
from ..services import SecurityService


class UserResource(ModelResource):
    """
    RESTful API resource for the :class:`~flask_unchained.bundles.security.User` model.
    """

    security_service: SecurityService = injectable

    class Meta:
        model = User
        include_methods = {CREATE, GET, PATCH}
        method_decorators = {
            CREATE: [anonymous_user_required],
            GET: [auth_required_same_user],
            PATCH: [auth_required_same_user],
        }

    # skipcq: PYL-W0221 (parameters mismatch in overridden method)
    def create(self, user, errors):
        if errors:
            return self.errors(errors)

        user_logged_in = self.security_service.register_user(user)
        if user_logged_in:
            return self.created({'token': user.get_auth_token(),
                                 'user': user}, commit=False)
        return self.created({'user': user}, commit=False)
