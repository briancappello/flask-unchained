class AwesomeExtension:
    def __init__(self, app=None):
        self.app = app
        self.name = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.name = 'awesome!'


awesome = AwesomeExtension()


EXTENSIONS = {
    'awesome': awesome,
}
