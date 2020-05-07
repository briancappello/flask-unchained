from flask_unchained import Service
from flask_unchained.di import ServiceMetaclass
from sqlalchemy_unchained.session_manager import (SessionManager as BaseSessionManager,
                                                  SessionManagerMetaclass as BaseSessionManagerMetaclass)


class SessionManagerMetaclass(ServiceMetaclass, BaseSessionManagerMetaclass):
    pass


class SessionManager(BaseSessionManager, Service, metaclass=SessionManagerMetaclass):
    """
    The database session manager service.
    """
