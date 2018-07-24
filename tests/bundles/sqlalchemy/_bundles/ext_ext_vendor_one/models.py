from ..vendor_one.models import (
    OneUser as BaseOneUser,
    OneRole as BaseOneRole,
)


class OneUser(BaseOneUser):
    class Meta:
        lazy_mapped = True


class OneRole(BaseOneRole):
    class Meta:
        lazy_mapped = True
