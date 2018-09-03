# These commands are adapted to click from Flask-Script 0.4.0 (and extended)
import inspect

from flask_unchained import current_app
from flask_unchained.cli import click, with_appcontext
from typing import *
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.routing import Rule

from .utils import print_table


@click.command()
@click.argument('url')
@click.option('--method', default='GET',
              help='Method for url to match (default: GET)')
@with_appcontext
def url(url: str, method: str):
    """Show details for a specific URL."""
    try:
        url_rule, params = (current_app.url_map.bind('localhost')
                            .match(url, method=method, return_rule=True))
    except (NotFound, MethodNotAllowed)\
            as e:
        click.secho(str(e), fg='white', bg='red')
    else:
        headings = ('Method(s)', 'Rule', 'Params', 'Endpoint', 'View', 'Options')
        print_table(headings,
                    [(_get_http_methods(url_rule),
                      url_rule.rule if url_rule.strict_slashes
                                    else url_rule.rule + '[/]',
                      _format_dict(params),
                      url_rule.endpoint,
                      _get_rule_view(url_rule),
                      _format_rule_options(url_rule))],
                    ['<' if i > 0 else '>' for i, col in enumerate(headings)],
                    primary_column_idx=1)


@click.command()
@click.option('--order-by', default='priority',
              help='Property to order by: methods, rule, endpoint, view, or '
                   'priority (aka registration order with the app)')
@with_appcontext
def urls(order_by: Optional[str] = None):
    """List all URLs registered with the app."""
    url_rules: List[Rule] = current_app.url_map._rules

    # sort the rules. by default they're sorted by priority,
    # ie in the order they were registered with the app
    if order_by == 'view':
        url_rules = sorted(url_rules, key=lambda rule: _get_rule_view(rule))
    elif order_by != 'priority':
        url_rules = sorted(url_rules, key=lambda rule: getattr(rule, order_by))

    headings = ('Method(s)', 'Rule', 'Endpoint', 'View', 'Options')
    print_table(headings,
                [(_get_http_methods(url_rule),
                  url_rule.rule if url_rule.strict_slashes
                                else url_rule.rule.rstrip('/') + '[/]',
                  url_rule.endpoint,
                  _get_rule_view(url_rule),
                  _format_rule_options(url_rule),
                  ) for url_rule in url_rules],
                ['<' if i > 0 else '>' for i, col in enumerate(headings)],
                primary_column_idx=1)


def _get_http_methods(url_rule: Rule) -> str:
    if url_rule.methods is None:
        return 'GET'

    methods = url_rule.methods.difference({'HEAD', 'OPTIONS'})
    return ', '.join(sorted(list(methods)))


def _get_rule_view(url_rule: Rule) -> str:
    try:
        view_fn = current_app.view_functions[url_rule.endpoint]
    except KeyError:
        return '(None)'

    view_class = getattr(view_fn, 'view_class', None)
    view_module = inspect.getmodule(view_class if view_class else view_fn)

    view_fn_name = view_fn.__name__
    if '.as_view.' in view_fn.__qualname__:
        view_fn_name = view_class.__name__
    elif '.method_as_view.' in view_fn.__qualname__:
        view_fn_name = f'{view_class.__name__}.{view_fn.__name__}'

    return f'{view_module.__name__} :: {view_fn_name}'


def _format_rule_options(url_rule: Rule) -> str:
    options = {}

    if url_rule.strict_slashes:
        options['strict_slashes'] = True

    if url_rule.subdomain:
        options['subdomain'] = url_rule.subdomain

    if url_rule.host:
        options['host'] = url_rule.host

    return _format_dict(options)


def _format_dict(d: dict) -> str:
    rv = ''
    for key, value in sorted(d.items(), key=lambda item: item[0]):
        if value is True:
            rv += f'{key}; '
        else:
            rv += f'{key}: {value}; '
    return rv.rstrip('; ')
