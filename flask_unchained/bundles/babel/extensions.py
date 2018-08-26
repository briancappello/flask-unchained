from flask_babelex import Babel


babel = Babel()


EXTENSIONS = {
    'babel': babel,
}


__all__ = [
    'babel',
    'Babel',
]
