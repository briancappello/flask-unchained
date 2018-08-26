from .session import Session


session = Session()


EXTENSIONS = {
    'session': session,
}


__all__ = [
    'session',
    'Session',
]
