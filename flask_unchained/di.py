from .utils import snake_case


def ensure_service_name(service, name=None):
    name = name or getattr(service, '__di_name__', snake_case(service.__name__))

    try:
        setattr(service, '__di_name__', name)
    except AttributeError:
        pass  # must be a basic type, like str or int
        # (why anybody would do that is another issue, but it's not our problem)

    return name


class ServiceMeta(type):
    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        if '__abstract__' in clsdict:
            return

        if '__init__' in clsdict:
            from .unchained import unchained
            cls.__init__ = unchained.inject()(clsdict['__init__'])

        ensure_service_name(cls)


class BaseService(metaclass=ServiceMeta):
    __abstract__ = True
