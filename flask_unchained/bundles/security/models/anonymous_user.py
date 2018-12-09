from flask_login import AnonymousUserMixin
from werkzeug.datastructures import ImmutableList


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.roles = ImmutableList()

    @property
    def id(self):
        return None

    @property
    def active(self):
        return False

    def has_role(self, *args):
        return False
