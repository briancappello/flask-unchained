from flask_unchained import AppBundle, FlaskUnchained, generate_csrf


class App(AppBundle):
    def after_init_app(self, app: FlaskUnchained):
        @app.after_request
        def set_csrf_token_cookie(response):
            if response:
                response.set_cookie('csrf_token', generate_csrf())
            return response
