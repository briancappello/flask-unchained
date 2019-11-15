from .cors import CORS


cors = CORS()


EXTENSIONS = {
    'cors': cors,
}


__all__ = [
    'cors',
    'CORS',
]
