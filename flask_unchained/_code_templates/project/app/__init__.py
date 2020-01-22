from flask_unchained import AppBundle, FlaskUnchained, generate_csrf


class App(AppBundle):
    @classmethod
    def after_init_app(cls, app: FlaskUnchained):
        app.jinja_env.add_extension('jinja2_time.TimeExtension')

        @app.after_request
        def set_csrf_token_cookie(response):
            if response:
                response.set_cookie('csrf_token', generate_csrf())
            return response
