from .oauth import OAuth


oauth = OAuth()


EXTENSIONS = {
    'oauth': (oauth, ['security']),
}


__all__ = [
    'oauth',
    'OAuth',
]
