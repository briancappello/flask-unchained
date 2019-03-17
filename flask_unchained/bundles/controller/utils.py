import re

from flask import (Response, current_app, request, redirect as flask_redirect,
                   url_for as flask_url_for)
from flask_unchained.string_utils import kebab_case, right_replace, snake_case
from py_meta_utils import _missing
from typing import *
from urllib.parse import urlsplit
from werkzeug.local import LocalProxy
from werkzeug.routing import BuildError, UnicodeConverter

from .attr_constants import CONTROLLER_ROUTES_ATTR, REMOVE_SUFFIXES_ATTR


PARAM_NAME_RE = re.compile(r'<(\w+:)?(?P<param_name>\w+)>')
LAST_PARAM_NAME_RE = re.compile(r'<(\w+:)?(?P<param_name>\w+)>$')


class StringConverter(UnicodeConverter):
    """
    This converter is the default converter and accepts any string but
    only one path segment.  Thus the string can not include a slash.

    This is the default validator.

    Example::

        Rule('/pages/<page>'),
        Rule('/<string(length=2):lang_code>')

    :param map: the :class:`Map`.
    :param minlength: the minimum length of the string.  Must be greater
                      or equal 1.
    :param maxlength: the maximum length of the string.
    :param length: the exact length of the string.
    """
    def __init__(self, map, minlength=1, maxlength=None, length=None, upper=False):
        super().__init__(map, minlength, maxlength, length)
        self.is_upper = upper

    def to_python(self, value: str):
        if self.is_upper:
            return super().to_python(value).upper()
        return super().to_python(value)

    def to_url(self, value):
        if self.is_upper:
            return super().to_url(value).upper()
        return super().to_url(value)


def controller_name(cls, _remove_suffixes=None) -> str:
    """
    Returns the snake-cased name for a controller/resource class. Automatically
    strips ``Controller``, ``View``, and ``MethodView`` suffixes, eg::

        SiteController -> site
        FooBarBazView -> foo_bar_baz
        UsersMethodView -> users
    """
    name = cls if isinstance(cls, str) else cls.__name__
    remove_suffixes = _remove_suffixes or getattr(cls, REMOVE_SUFFIXES_ATTR)
    for suffix in remove_suffixes:
        if name.endswith(suffix):
            name = right_replace(name, suffix, '')
            break
    return snake_case(name)


def get_param_tuples(url_rule) -> List[Tuple[str, str]]:
    """
    Returns a list of parameter tuples in a URL rule, eg::

        url_rule = '/users/<string:username>/roles/<int:id>'
        param_tuples = get_param_tuples(url_rule)
        assert param_tuples == [('string', 'username'), ('int', 'id')]
    """
    if not url_rule:
        return []
    return [(type_[:-1], name) for type_, name
            in re.findall(PARAM_NAME_RE, url_rule)]


def get_last_param_name(url_rule) -> Union[str, None]:
    """
    Returns the name of the last parameter in a URL rule, eg::

        assert get_last_param_name('/foo/<int:id>/roles') is None

        url_rule = '/foo/<int:id>/bar/<any:something>/baz/<string:spam>'
        assert get_last_param_name(url_rule) == 'spam'
    """
    if not url_rule:
        return None
    match = re.search(LAST_PARAM_NAME_RE, url_rule)
    return match.group('param_name') if match else None


def url_for(endpoint_or_url_or_config_key: str,
            _anchor: Optional[str] = None,
            _cls: Optional[Union[object, type]] = None,
            _external: Optional[bool] = False,
            _external_host: Optional[str] = None,
            _method: Optional[str] = None,
            _scheme: Optional[str] = None,
            **values,
            ) -> Union[str, None]:
    """
    An improved version of flask's url_for function

    :param endpoint_or_url_or_config_key: what to lookup. it can be an endpoint
      name, an app config key, or an already-formed url. if _cls is specified,
      it also accepts a method name.
    :param values: the variable arguments of the URL rule
    :param _anchor: if provided this is added as anchor to the URL.
    :param _cls: if specified, can also pass a method name as the first argument
    :param _external: if set to ``True``, an absolute URL is generated. Server
      address can be changed via ``SERVER_NAME`` configuration variable which
      defaults to `localhost`.
    :param _external_host: if specified, the host of an external server
        to generate urls for (eg https://example.com or localhost:8888)
    :param _method: if provided this explicitly specifies an HTTP method.
    :param _scheme: a string specifying the desired URL scheme. The `_external`
      parameter must be set to ``True`` or a :exc:`ValueError` is raised. The
      default behavior uses the same scheme as the current request, or
      ``PREFERRED_URL_SCHEME`` from the :ref:`app configuration <config>` if no
      request context is available. As of Werkzeug 0.10, this also can be set
      to an empty string to build protocol-relative URLs.
    """
    what = endpoint_or_url_or_config_key

    # if what is a config key
    if what and what.isupper():
        what = current_app.config.get(what)

    if isinstance(what, LocalProxy):
        what = what._get_current_object()

    # if we already have a url (or an invalid value, eg None)
    if not what or '/' in what:
        return what

    flask_url_for_kwargs = dict(_anchor=_anchor, _external=_external,
                                _external_host=_external_host, _method=_method,
                                _scheme=_scheme, **values)

    # check if it's a class method name, and try that endpoint
    if _cls and '.' not in what:
        controller_routes = getattr(_cls, CONTROLLER_ROUTES_ATTR)
        method_routes = controller_routes.get(what)
        try:
            return _url_for(method_routes[0].endpoint, **flask_url_for_kwargs)
        except (
            BuildError,  # url not found
            IndexError,  # method_routes[0] is out-of-range
            TypeError,   # method_routes is None
        ):
            pass

    # what must be an endpoint
    return _url_for(what, **flask_url_for_kwargs)


def join(*args, trailing_slash=False):
    """
    Return a url path joined from the arguments. It correctly handles blank/None
    arguments, and removes back-to-back slashes, eg::

        assert join('/', 'foo', None, 'bar', '', 'baz') == '/foo/bar/baz'
        assert join('/', '/foo', '/', '/bar/') == '/foo/bar'

    Note that it removes trailing slashes by default, so if you want to keep those,
    then you need to pass the ``trailing_slash`` keyword argument::

        assert join('/foo', 'baz', None, trailing_slash=True) == '/foo/baz/'
    """
    dirty_path = '/'.join(map(lambda x: x and x or '', args))
    path = re.sub(r'/+', '/', dirty_path)
    if path in {'', '/'}:
        return '/'
    path = path.rstrip('/')
    return path if not trailing_slash else path + '/'


def method_name_to_url(method_name) -> str:
    """
    Converts a method name to a url.
    """
    return '/' + kebab_case(method_name).strip('-')


# modified from flask_security.utils.get_post_action_redirect
def redirect(where: Optional[str] = None,
             default: Optional[str] = None,
             override: Optional[str] = None,
             _anchor: Optional[str] = None,
             _cls: Optional[Union[object, type]] = None,
             _external: Optional[bool] = False,
             _external_host: Optional[str] = None,
             _method: Optional[str] = None,
             _scheme: Optional[str] = None,
             **values,
             ) -> Response:
    """
    An improved version of flask's redirect function

    :param where: A URL, endpoint, or config key name to redirect to
    :param default: A URL, endpoint, or config key name to redirect to if
      ``where`` is invalid
    :param override: explicitly redirect to a URL, endpoint, or config key name
      (takes precedence over the ``next`` value in query strings or forms)
    :param values: the variable arguments of the URL rule
    :param _anchor: if provided this is added as anchor to the URL.
    :param _cls: if specified, allows a method name to be passed to where,
      default, and/or override
    :param _external: if set to ``True``, an absolute URL is generated. Server
      address can be changed via ``SERVER_NAME`` configuration variable which
      defaults to `localhost`.
    :param _external_host: if specified, the host of an external server to
      generate urls for (eg https://example.com or localhost:8888)
    :param _method: if provided this explicitly specifies an HTTP method.
    :param _scheme: a string specifying the desired URL scheme. The `_external`
      parameter must be set to ``True`` or a :exc:`ValueError` is raised. The
      default behavior uses the same scheme as the current request, or
      ``PREFERRED_URL_SCHEME`` from the :ref:`app configuration <config>` if no
      request context is available. As of Werkzeug 0.10, this also can be set
      to an empty string to build protocol-relative URLs.
    """
    flask_url_for_kwargs = dict(_anchor=_anchor, _external=_external,
                                _external_host=_external_host, _method=_method,
                                _scheme=_scheme, **values)

    urls = [url_for(request.args.get('next'), **flask_url_for_kwargs),
            url_for(request.form.get('next'), **flask_url_for_kwargs)]
    if where:
        urls.append(url_for(where, _cls=_cls, **flask_url_for_kwargs))
    if default:
        urls.append(url_for(default, _cls=_cls, **flask_url_for_kwargs))
    if override:
        urls.insert(0, url_for(override, _cls=_cls, **flask_url_for_kwargs))

    for url in urls:
        if _validate_redirect_url(url, _external_host):
            return flask_redirect(url)
    return flask_redirect('/')


def rename_parent_resource_param_name(route, rule: str) -> str:
    ctrl_name = controller_name(route._parent_resource_cls)
    type_, orig_name = get_param_tuples(route._parent_member_param)[0]
    renamed_param = (route._unique_member_param
                     or f'<{type_}:{ctrl_name}_{orig_name}>')
    if renamed_param in rule:
        type_, orig_name = get_param_tuples(route.unique_member_param)[0]
        renamed_param = f'<{type_}:{ctrl_name}_{orig_name}>'
    return rule.replace(route._parent_member_param, renamed_param, 1)


def _missing_to_default(arg, default=None):
    return arg if arg is not _missing else default


def _url_for(endpoint: str, **values) -> Union[str, None]:
    """
    The same as flask's url_for, except this also supports building external
    urls for hosts that are different from app.config.SERVER_NAME. One case
    where this is especially useful is for single page apps, where the frontend
    is not hosted by the same server as the backend, but the backend still needs
    to generate urls to frontend routes

    :param endpoint: the name of the endpoint
    :param values: the variable arguments of the URL rule
    :return: a url path, or None
    """
    _external_host = values.pop('_external_host', None)
    is_external = bool(_external_host or values.get('_external'))
    external_host = _external_host or current_app.config.get('EXTERNAL_SERVER_NAME')
    if not is_external or not external_host:
        return flask_url_for(endpoint, **values)

    if '://' not in external_host:
        external_host = f'http://{external_host}'
    values.pop('_external')
    return external_host.rstrip('/') + flask_url_for(endpoint, **values)


# modified from flask_security.utils.validate_redirect_url
def _validate_redirect_url(url, _external_host=None):
    if url is None or url.strip() == '':
        return False
    url_next = urlsplit(url)
    url_base = urlsplit(request.host_url)
    external_host = _external_host or current_app.config.get('EXTERNAL_SERVER_NAME', '')
    if ((url_next.netloc or url_next.scheme)
            and url_next.netloc != url_base.netloc
            and url_next.netloc not in external_host):
        return False
    return True


__all__ = [
    'controller_name',
    'get_last_param_name',
    'get_param_tuples',
    'join',
    'method_name_to_url',
    'redirect',
    'rename_parent_resource_param_name',
    'url_for',
]
