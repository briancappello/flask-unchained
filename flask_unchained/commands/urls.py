# These commands are adapted to click from Flask-Script 0.4.0 (and extended)

import click
import inspect

from flask import current_app
from flask.cli import cli
from werkzeug.exceptions import MethodNotAllowed, NotFound

from .utils import print_table


@cli.command()
@click.argument('url')
@click.option('--method', default='GET',
              help='Method for url to match (default: GET)')
def url(url, method):
    """Show details for a specific URL."""
    try:
        rule, params = (current_app.url_map
                           .bind('localhost')
                           .match(url, method=method, return_rule=True))
    except (NotFound, MethodNotAllowed) as e:
        click.echo(str(e))
    else:
        headings = ('', 'Rule', 'Params', 'Endpoint', 'View', 'Options')
        print_table(headings,
                    [(_get_http_methods(rule),
                      rule.rule,
                      _format_dict(params),
                      rule.endpoint,
                      _get_rule_view(rule),
                      _format_rule_options(rule))],
                    ['<' if col else '>' for col in headings])


@cli.command()
@click.option('--order', default=None,
              help='Property on Rule to order by '
                   '(default: app registration order)')
def urls(order=None):
    """List all URLs registered with the app."""
    rules = current_app.url_map._rules
    if order is not None:
        rules = sorted(rules, key=lambda rule: getattr(rule, order))

    headings = ('', 'Rule', 'Endpoint', 'View', 'Options')
    print_table(headings,
                [(_get_http_methods(rule),
                  rule.rule,
                  rule.endpoint,
                  _get_rule_view(rule),
                  _format_rule_options(rule),
                  ) for rule in rules],
                ['<' if col else '>' for col in headings])


def _get_http_methods(url_rule):
    if url_rule.methods is None:
        return 'GET'

    methods = url_rule.methods.difference({'HEAD', 'OPTIONS'})
    return ', '.join(sorted(list(methods)))


def _get_rule_view(rule):
    view_fn = current_app.view_functions[rule.endpoint]
    view_class = getattr(view_fn, 'view_class', None)
    view_module = inspect.getmodule(view_class if view_class else view_fn)

    view_fn_name = view_fn.__name__
    if '.as_view.' in view_fn.__qualname__:
        view_fn_name = view_class.__name__
    elif '.method_as_view.' in view_fn.__qualname__:
        view_fn_name = f'{view_class.__name__}.{view_fn.__name__}'

    return f'{view_module.__name__}:{view_fn_name}'


def _format_rule_options(url_rule):
    options = {}

    # FIXME: when not strict_slashes, maybe print the rule as something like:
    # /foo/bar[/] or perhaps /foo/bar[/ -> '']
    if url_rule.strict_slashes:
        options['strict_slashes'] = True

    if url_rule.subdomain:
        options['subdomain'] = url_rule.subdomain

    if url_rule.host:
        options['host'] = url_rule.host

    return _format_dict(options)


def _format_dict(d):
    ret = ''
    for key, value in sorted(d.items(), key=lambda item: item[0]):
        if value is True:
            ret += f'{key}; '
        else:
            ret += f'{key}: {value}; '
    return ret.rstrip('; ')
