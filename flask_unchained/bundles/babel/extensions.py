from flask_babel import Babel


babel = Babel()


EXTENSIONS = {
    "babel": babel,
}


__all__ = [
    "babel",
    "Babel",
]
