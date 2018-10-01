from .security import Security


security = Security()


EXTENSIONS = {
    'security': (security, ['csrf', 'db'])
}


__all__ = [
    'security',
    'Security',
]
