from flask_unchained import Controller, route


class SiteController(Controller):
    @route('/')
    def index(self):
        return self.render('index')
