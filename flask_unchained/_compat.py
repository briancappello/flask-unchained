import functools
import inspect


# *************************************************************************
# monkey patch functools.wraps to assign __signature__ by default
# *************************************************************************

def update_wrapper(wrapper,
                   wrapped,
                   assigned=None,
                   updated=None):
    wrapper = functools.update_wrapper(
        wrapper,
        wrapped,
        assigned or tuple(list(functools.WRAPPER_ASSIGNMENTS) + [
            '__signature__',
        ]),
        updated or functools.WRAPPER_UPDATES,
    )

    if not hasattr(wrapper, '__signature__'):
        try:
            wrapper.__signature__ = inspect.signature(wrapped)
        except ValueError:
            pass

    return wrapper


def wraps(wrapped_fn, assigned=None, updated=None):
    return functools.partial(update_wrapper, wrapped=wrapped_fn,
                             assigned=assigned, updated=updated)


setattr(functools, 'wraps', wraps)


# *************************************************************************
# quart asyncio integration [optional]
# *************************************************************************

# FIXME can we somehow make this a callback loaded from an optional env var?
# goals:
# - set base class to use for FlaskUnchained
# - set the LocalProxy class and the is_local_proxy fn
# - a place for any other necessary monkey patching

QUART_ENABLED = False

from werkzeug.local import LocalProxy as WerkzeugLocalProxy
LocalProxy = WerkzeugLocalProxy

try:
    import quart.flask_patch
    from quart.local import LocalProxy as QuartLocalProxy
except ImportError:
    QuartLocalProxy = type('QuartLocalProxy', (), {})
else:
    QUART_ENABLED = True
    LocalProxy = QuartLocalProxy


def is_local_proxy(obj) -> bool:
    return isinstance(obj, (WerkzeugLocalProxy, QuartLocalProxy))
