from flask_unchained import AppBundle, FlaskUnchained


class App(AppBundle):
    @classmethod
    def after_init_app(cls, app: FlaskUnchained):
        app.jinja_env.add_extension('jinja2_time.TimeExtension')
