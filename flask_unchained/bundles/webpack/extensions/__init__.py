from .webpack import Webpack


webpack = Webpack()


EXTENSIONS = {
    'webpack': webpack,
}


__all__ = [
    'webpack',
    'Webpack',
]
