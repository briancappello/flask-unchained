from flask_unchained import AppBundle as BaseAppBundle


class AppBundle(BaseAppBundle):
    blueprint_names = ['one', 'two']
