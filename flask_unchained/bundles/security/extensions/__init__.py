from flask_wtf import CSRFProtect

from .security import Security


csrf = CSRFProtect()
security = Security()


EXTENSIONS = {
    'csrf': csrf,
    'security': (security, ['csrf', 'db'])
}


__all__ = [
    'csrf',
    'CSRFProtect',
    'security',
    'Security',
]
