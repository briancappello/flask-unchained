from .security_controller import SecurityController

try:
    from .user_resource import UserResource
except ImportError:
    UserResource = None
