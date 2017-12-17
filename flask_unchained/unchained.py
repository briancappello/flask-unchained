class Unchained:
    def __init__(self, app=None):
        self.app = app

        self._registered_extensions = {}
        self.models = {}
        self.serializers = {}
        self.services = {}

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.extensions['unchained'] = self
        setattr(app, 'unchained', self)

    def __getattr__(self, name):
        for store in ('models', 'serializers', 'services'):
            d = getattr(self, store)
            if name in d:
                return d[name]
        raise AttributeError(name)


unchained = Unchained()
