class MyExtension:
    def __init__(self, app=None):
        self.app = app
        self.name = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.name = 'my ext!'


myext = MyExtension()


EXTENSIONS = {
    'myext': (myext, ['awesome']),
}
