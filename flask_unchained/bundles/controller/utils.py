import re

from flask import (
    Response,
    current_app as app,
    redirect as flask_redirect,
    request,
    url_for as flask_url_for,
)
from flask_unchained.string_utils import kebab_case, right_replace, snake_case
from typing import *
from urllib.parse import urlsplit
from werkzeug.local import LocalProxy
from werkzeug.routing import BuildError

from .attr_constants import CONTROLLER_ROUTES_ATTR, REMOVE_SUFFIXES_ATTR
from .constants import _missing


PARAM_NAME_RE = re.compile(r'<(\w+:)?(?P<param_name>\w+)>')
LAST_PARAM_NAME_RE = re.compile(r'<(\w+:)?(?P<param_name>\w+)>$')


def controller_name(cls) -> str:
    name = cls.__name__
    for suffix in getattr(cls, REMOVE_SUFFIXES_ATTR):
        if name.endswith(suffix):
            name = right_replace(name, suffix, '')
            break
    return snake_case(name)


def get_param_tuples(url_rule) -> List[Tuple[str, str]]:
    if not url_rule:
        return []
    return [(type_[:-1], name) for type_, name
            in re.findall(PARAM_NAME_RE, url_rule)]


def get_last_param_name(url_rule) -> Optional[str]:
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
        what = app.config.get(what)

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
    Return a url path joined from the arguments

    (correctly handles blank/None arguments, and removes back-to-back slashes)
    """
    dirty_path = '/'.join(map(lambda x: x and x or '', args))
    path = re.sub(r'/+', '/', dirty_path)
    if path in {'', '/'}:
        return '/'
    path = path.rstrip('/')
    return path if not trailing_slash else path + '/'


def method_name_to_url(method_name) -> str:
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


def _missing_to_default(arg, default=None):
    return arg if arg is not _missing else default


def _url_for(endpoint: str, **values) -> Union[str, None]:
    """
    The same as flask's url_for, except this also supports building external
    urls for hosts that are different from app.config['SERVER_NAME']. One case
    where this is especially useful is for single page apps, where the frontend
    is not hosted by the same server as the backend, but the backend still needs
    to generate urls to frontend routes

    :param endpoint: the name of the endpoint
    :param values: the variable arguments of the URL rule
    :return: a url path, or None
    """
    _external_host = values.pop('_external_host', None)
    is_external = bool(_external_host or values.get('_external'))
    external_host = (_external_host or app.config.get('EXTERNAL_SERVER_NAME'))
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
    external_host = _external_host or app.config.get('EXTERNAL_SERVER_NAME') or ''
    if ((url_next.netloc or url_next.scheme)
            and url_next.netloc != url_base.netloc
            and url_next.netloc not in external_host):
        return False
    return True
