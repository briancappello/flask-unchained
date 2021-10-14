from flask_unchained import AppBundle, FlaskUnchained


class App(AppBundle):
    def before_init_app(self, app: FlaskUnchained) -> None:
        app.url_map.strict_slashes = False
