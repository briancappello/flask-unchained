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

QUART_ENABLED = False
try:
    import quart.flask_patch
    from quart.local import LocalProxy as QuartLocalProxy
    QUART_ENABLED = True
except ImportError:
    QuartLocalProxy = type('QuartLocalProxy', (), {})

from werkzeug.local import LocalProxy as WerkzeugLocalProxy


def is_local_proxy(obj) -> bool:
    return isinstance(obj, (WerkzeugLocalProxy, QuartLocalProxy))
