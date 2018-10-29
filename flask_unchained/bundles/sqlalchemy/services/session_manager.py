from flask_unchained import BaseService
from flask_unchained.di import ServiceMeta
from sqlalchemy_unchained.session_manager import (SessionManager as _SessionManager,
                                                  _SessionManagerMetaclass)


class SessionManagerMetaclass(ServiceMeta, _SessionManagerMetaclass):
    pass


class SessionManager(_SessionManager, BaseService, metaclass=SessionManagerMetaclass):
    """
    The database session manager service.
    """
