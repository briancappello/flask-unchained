from flask_unchained import Controller, route, injectable, current_app

from .extensions import Api


class OpenAPIController(Controller):
    class Meta:
        url_prefix = '/docs'

    api: Api = injectable

    @route('/')
    def redoc(self):
        return self.render('redoc', redoc_url=current_app.config.API_REDOC_SOURCE_URL)

    @route('/openapi.json')
    def json(self):
        return self.jsonify(self.api.spec.to_dict())
