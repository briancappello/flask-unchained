from flask_login import AnonymousUserMixin
from werkzeug.datastructures import ImmutableList


class AnonymousUser(AnonymousUserMixin):
    _sa_instance_state = None

    def __init__(self):
        self.roles = ImmutableList()

    @property
    def id(self):
        return None

    def has_role(self, *args):
        return False
