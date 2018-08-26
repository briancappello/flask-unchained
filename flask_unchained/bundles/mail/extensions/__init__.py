from .mail import Mail


mail = Mail()


EXTENSIONS = {
    'mail': mail,
}


__all__ = [
    'mail',
    'Mail',
]
