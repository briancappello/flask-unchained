from ..vendor_one.models import OneRole as BaseOneRole
from ..vendor_one.models import OneUser as BaseOneUser


class OneUser(BaseOneUser):
    class Meta:
        lazy_mapped = True


class OneRole(BaseOneRole):
    class Meta:
        lazy_mapped = True
