from flask_unchained import BaseService
from flask_unchained.di import ServiceMeta
from sqlalchemy_unchained.session_manager import (SessionManager as _SessionManager,
                                                  _SessionMetaclass)


class SessionManagerServiceMetaclass(ServiceMeta, _SessionMetaclass):
    pass


class SessionManager(_SessionManager, BaseService,
                     metaclass=SessionManagerServiceMetaclass):
    """
    The session manager.
    """
