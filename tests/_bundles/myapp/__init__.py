from flask_unchained import AppBundle

from .extensions import myext


class MyAppBundle(AppBundle):
    command_group_names = ('goo_group',)
