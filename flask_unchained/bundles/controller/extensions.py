from flask_wtf import CSRFProtect


csrf = CSRFProtect()


EXTENSIONS = {
    'csrf': csrf,
}


__all__ = [
    'csrf',
    'CSRFProtect',
]
