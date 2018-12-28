"""
Extend Flask's template loading support to allow overriding/extending/including
templates with the same name/path as templates from later template folders (ie
from superclass bundles in the hierarchy)
"""
import re

from flask import request
from flask.templating import DispatchingJinjaLoader, Environment
from flask_unchained import unchained
from jinja2 import TemplateNotFound
from typing import *


TEMPLATE_OVERRIDE_RE = re.compile(r'^(?P<template>.+)__(?P<depth>\d+)__$')


def parse_template(template):
    """returns a 2-tuple of (template_name, number_of_priors)"""
    m = TEMPLATE_OVERRIDE_RE.match(template)
    if not m:
        return template, 0
    return m.group('template'), int(m.group('depth'))


class UnchainedJinjaEnvironment(Environment):
    def join_path(self, template, parent):
        parent, depth = parse_template(parent)
        if template == parent:
            return f'{template}__{depth + 1}__'
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


def pretty_num(num):
    if num % 10 == 1 and num != 11:
        return f'{num}st'
    elif num % 10 == 2 and num != 12:
        return f'{num}nd'
    elif num % 10 == 3 and num != 13:
        return f'{num}rd'
    else:
        return f'{num}th'


def explain_template_loading_attempts(app, template, attempts):
    """
    This should help developers understand what failed. Mostly the same as
    :func:`flask.debughelpers.explain_template_loading_attempts`, except here we've
    extended it to support showing what :class:`UnchainedJinjaLoader` is doing.
    """
    from flask import Flask, Blueprint
    from flask.debughelpers import _dump_loader_info
    from flask.globals import _request_ctx_stack

    template, expected_priors = parse_template(template)
    info = [f'Locating {pretty_num(expected_priors + 1)} template "{template}":']

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
def is_active(endpoint_or_kwargs: Union[str, dict]):
    endpoint = None
    href = None
    if isinstance(endpoint_or_kwargs, str):
        if '/' in endpoint_or_kwargs:
            href = endpoint_or_kwargs
        else:
            endpoint = endpoint_or_kwargs
    elif isinstance(endpoint_or_kwargs, dict):
        endpoint = endpoint_or_kwargs.get('endpoint')
        href = endpoint_or_kwargs.get('href')
    else:
        raise TypeError('the first argument to is_active must be a str or dict')

    if endpoint:
        return endpoint == request.endpoint

    return href == request.path or href == request.url
