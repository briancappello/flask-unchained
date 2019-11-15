from flask_cors import CORS as BaseCORS


class CORS(object):
    def init_app(self, app):
        BaseCORS(app)
