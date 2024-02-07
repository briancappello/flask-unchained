from .session import Session


session = Session()


EXTENSIONS = {
    "session": (session, ["db"]),
}


__all__ = [
    "session",
    "Session",
]
