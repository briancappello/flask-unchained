"""
Extends Flask's template loading support to allow overriding/extending/including
templates with the same name as templates from later template folders
"""
import re

from flask import request
from flask.templating import DispatchingJinjaLoader, Environment
from flask_unchained import unchained
from jinja2 import TemplateNotFound


TEMPLATE_OVERRIDE_RE = re.compile(r'^(?P<template>.+)__(?P<depth>\d+)__$')


def parse_template(template):
    """returns a 2-tuple of (template_name, number_of_priors)"""
    m = TEMPLATE_OVERRIDE_RE.match(template)
    if not m:
        return template, 0
    return m.group('template'), int(m.group('depth'))


def make_template_override(template, depth):
    return f'{template}__{depth + 1}__'


class UnchainedJinjaEnvironment(Environment):
    def join_path(self, template, parent):
        parent, depth = parse_template(parent)
        if template == parent:
            return make_template_override(template, depth)
        return template


class UnchainedJinjaLoader(DispatchingJinjaLoader):
    def _get_source_explained(self, environment, template):
        attempts = []
        trv = None
        original_template = template
        num_priors = 0
        template, expected_priors = parse_template(template)

        for srcobj, loader in self._iter_loaders(template):
            try:
                rv = loader.get_source(environment, template)
            except TemplateNotFound:
                rv = None

            if expected_priors - num_priors == 0:
                trv = rv
            if rv:
                num_priors += 1

            attempts.append((loader, srcobj, rv))

        explain_template_loading_attempts(self.app, original_template, attempts)

        if trv is not None:
            return trv
        raise TemplateNotFound(template)

    def _get_source_fast(self, environment, template):
        num_priors = 0
        template, expected_priors = parse_template(template)

        for srcobj, loader in self._iter_loaders(template):
            try:
                rv = loader.get_source(environment, template)
            except TemplateNotFound:
                continue

            if expected_priors - num_priors == 0:
                return rv
            num_priors += 1

        raise TemplateNotFound(template)


def pretty_num(depth):
    depth += 1
    if depth == 1:
        return '1st'
    elif depth == 2:
        return '2nd'
    elif depth == 3:
        return '3rd'
    else:
        return depth + 'th'


def explain_template_loading_attempts(app, template, attempts):
    """This should help developers understand what failed"""
    from flask import Flask, Blueprint
    from flask.debughelpers import _dump_loader_info
    from flask.globals import _request_ctx_stack

    template, expected_priors = parse_template(template)
    info = ['Locating %s template "%s":' % (pretty_num(expected_priors),
                                            template)]

    total_found = 0
    blueprint = None
    reqctx = _request_ctx_stack.top
    if reqctx is not None and reqctx.request.blueprint is not None:
        blueprint = reqctx.request.blueprint

    for idx, (loader, srcobj, triple) in enumerate(attempts):
        if isinstance(srcobj, Flask):
            src_info = 'application "%s"' % srcobj.import_name
        elif isinstance(srcobj, Blueprint):
            src_info = 'blueprint "%s" (%s)' % (srcobj.name,
                                                srcobj.import_name)
        else:
            src_info = repr(srcobj)

        info.append('% 5d: trying loader of %s' % (
            idx + 1, src_info))

        for line in _dump_loader_info(loader):
            info.append('       %s' % line)

        if triple is None:
            detail = 'no match'
        else:
            if total_found < expected_priors:
                action = 'skipping'
            elif total_found == expected_priors:
                action = 'using'
            else:
                action = 'ignoring'
            detail = '%s (%r)' % (action, triple[1] or '<string>')
            total_found += 1

        info.append('       -> %s' % detail)

    seems_fishy = False
    if total_found < expected_priors:
        info.append('Error: the template could not be found.')
        seems_fishy = True

    if blueprint is not None and seems_fishy:
        info.append('  The template was looked up from an endpoint that '
                    'belongs to the blueprint "%s".' % blueprint)
        info.append('  Maybe you did not place a template in the right folder?')
        info.append('  See http://flask.pocoo.org/docs/blueprints/#templates')

    app.logger.info('\n'.join(info))


@unchained.template_test(name='active')
def is_active(endpoint):
    return request.endpoint == endpoint
