import os
import re
import shutil
import sys

from flask_unchained.cli import click
from flask_unchained.click import default, skip_prompting
from flask_unchained.string_utils import right_replace
from jinja2 import Environment
from typing import *


JINJA_START_STR = '{#!'
JINJA_END_STR = '#}'
OTHER_START_STR = '#! '
OTHER_INLINE_START_STR = '#!('
OTHER_INLINE_END_STR = ')'


env = Environment()
_excluded = object()

MODULE_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
IF_RE = re.compile(r'^if (?P<condition>.+): ?(?P<statement>.+)?$')
ELIF_RE = re.compile(r'^elif (?P<condition>.+): ?(?P<statement>.+)?$')
ELSE_RE = re.compile(r'^else: ?(?P<statement>.+)?$')

TEMPLATES_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, '_code_templates'))
PROJECT_TEMPLATE = os.path.join(TEMPLATES_ROOT, 'project')


def _validate_module_name(ctx, param, value):
    try:
        assert MODULE_NAME_RE.match(value) is not None
        return value
    except AssertionError:
        raise click.BadParameter('must be a valid python module name '
                                 '(letters, numbers, and underscore characters only)')


class Token:
    def __init__(self, line_num=0, token=None):
        self._line_num = line_num
        self.tokens = []
        if token is not None:
            self.tokens.append(token)

    @property
    def line_num(self):
        return self._line_num + 1

    @line_num.setter
    def line_num(self, line_num):
        self._line_num = line_num - 1

    def render(self, ctx=None, *, _debug=False):
        if len(self.tokens) == 1:
            token = self.tokens[0]
            if isinstance(token, str):
                return token if not _debug else f'{self.line_num}: {token}'
            return token.render(ctx, _debug=_debug)

        lines = []
        for t in self.tokens:
            result = t.render(ctx, _debug=_debug)
            if result is not _excluded:
                lines.append(result)
        return '\n'.join(lines)

    def __repr__(self):
        return f'{self.__class__.__name__}(tokens=\n{self.tokens!r})'


class InlineToken(Token):
    def __init__(self, line_num, parts):
        super().__init__(line_num)
        self.tokens = parts

    def render(self, ctx=None, *, _debug=False):
        if len(self.tokens) == 1:
            if isinstance(self.tokens[0], (str, InlineToken)):
                return env.from_string(self.tokens[0]).render(**ctx)
            return super().render(ctx, _debug=_debug)

        parts = []
        for t in self.tokens:
            if isinstance(t, str):
                parts.append(t)
                continue

            result = t.render(ctx, _debug=_debug)
            if result is not _excluded:
                parts.append(result)

        return ('' if not _debug else f'{self.line_num}: ') + ''.join(parts)

    def __str__(self):
        if len(self.tokens) > 1:
            return ''.join(str(t) for t in self.tokens)
        return self.tokens[0]


class IfToken(Token):
    def __init__(self, line_num, condition, statement):
        super().__init__(line_num)
        self.condition = condition
        self.statement = statement
        self.next = None

    def render(self, ctx=None, *, _debug=False):
        condition = (self.condition if isinstance(self.condition, (str, bytes))
                     else repr(self.condition))
        if not eval(condition, env.globals, ctx):
            if self.next:
                return self.next.render(ctx, _debug=_debug)
            return _excluded

        if self.statement:
            result = env.from_string(self.statement).render(**ctx)
            return result if not _debug else f'{self.line_num}: {result}'
        else:
            return super().render(ctx, _debug=_debug)

    def __repr__(self):
        return f'IfToken(cond={self.condition!r}, token={self.tokens[0]!r}, next={self.next!r})'


@click.group()
def new():
    """
    Generate new code for your Flask Unchained projects.
    """


@new.command()
@click.argument('dest', type=click.Path(resolve_path=True),
                help='The project folder.')
@click.option('-a', '--app-bundle', default='app',
              help='The module name to use for your app bundle.',
              callback=_validate_module_name)
@click.option('--force/--no-force', default=False, show_default=True,
              help='Whether or not to force creation if project folder is not empty.')
@click.option('--no-prompt', is_eager=True, is_flag=True, expose_value=False,
              help='Whether or not to skip prompting and just use the defaults.',
              default=False, show_default=True,
              callback=skip_prompting)
@click.option('--dev/--no-dev', prompt='Development Mode',
              help='Whether or not to install development dependencies.',
              default=lambda: default(True), show_default=True)
@click.option('--admin/--no-admin', prompt='Admin Bundle',
              help='Whether or not to install the Admin Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--api/--no-api', prompt='API Bundle',
              help='Whether or not to install the API Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--celery/--no-celery', prompt='Celery Bundle',
              help='Whether or not to install the Celery Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--graphene/--no-graphene', prompt='Graphene Bundle',
              help='Whether or not to install the Graphene Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--mail/--no-mail', prompt='Mail Bundle',
              help='Whether or not to install the Mail Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--oauth/--no-oauth', prompt='OAuth Bundle',
              help='Whether or not to install the OAuth Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--security/--no-security', prompt='Security Bundle',
              help='Whether or not to install the Security Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--session/--no-session', prompt='Session Bundle',
              help='Whether or not to install the Session Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--sqlalchemy/--no-sqlalchemy', prompt='SQLAlchemy Bundle',
              help='Whether or not to install the SQLAlchemy Bundle.',
              default=lambda: default(False), show_default=True)
@click.option('--webpack/--no-webpack', prompt='Webpack Bundle',
              help='Whether or not to install the Webpack Bundle.',
              default=lambda: default(False), show_default=True)
def project(dest, app_bundle, force, dev,
            admin, api, celery, graphene, mail, oauth,
            security, session, sqlalchemy, webpack):
    """
    Create a new Flask Unchained project.
    """
    if os.path.exists(dest) and os.listdir(dest) and not force:
        if not click.confirm(f'WARNING: Project directory {dest!r} exists and is '
                             f'not empty. It will be DELETED!!! Continue?'):
            click.echo(f'Exiting.')
            sys.exit(1)

    # build up a list of dependencies
    # IMPORTANT: keys here must match setup.py's `extra_requires` keys
    ctx = dict(dev=dev, admin=admin, api=api, celery=celery, graphene=graphene,
               mail=mail, oauth=oauth, security=security or oauth, session=security or session,
               sqlalchemy=security or sqlalchemy, webpack=webpack)
    ctx['requirements'] = [k for k, v in ctx.items() if v]

    # remaining ctx vars
    ctx['app_bundle_module_name'] = app_bundle

    # copy the project template into place
    copy_file_tree(PROJECT_TEMPLATE, dest, ctx, [
        (option, files)
        for option, files
        in [('api', ['app/serializers']),
            ('celery', ['app/tasks',
                        'celery_app.py']),
            ('graphene', ['app/graphql']),
            ('mail', ['templates/email']),
            ('security', ['app/models/role.py',
                          'app/models/user.py',
                          'db/fixtures/Role.yaml',
                          'db/fixtures/User.yaml']),
            ('webpack', ['assets',
                         'package.json',
                         'webpack']),
            ]
        if not ctx[option]
    ])

    click.echo(f'Successfully created a new project at: {dest}')


def copy_file_tree(src: str,
                   dest: str,
                   ctx: Optional[Dict[str, Any]] = None,
                   option_locations: Optional[List[Tuple[str, List[str]]]] = None):
    """
    Copy the file tree under the :param:`src` directory to the :param:`dest`
    directory. Pass :param:`ctx` to support rendering the files, and pass
    :param:`option_locations` to support deleting optional files/folders.
    """
    if os.path.exists(dest):
        shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest)

    if option_locations:
        for option, paths in option_locations:
            for path in paths:
                path = os.path.join(dest, path)
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path, ignore_errors=True)

    if 'app_bundle_module_name' in ctx:
        shutil.move(os.path.join(dest, 'app'),
                    os.path.join(dest, ctx['app_bundle_module_name']))
        shutil.move(os.path.join(dest, 'tests', 'app'),
                    os.path.join(dest, 'tests', ctx['app_bundle_module_name']))

    _render_file_tree(dest, ctx)


def _render_file_tree(root_dir: str, ctx: Optional[Dict[str, Any]] = None):
    if not ctx:
        return

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if ('__pycache__' in path
                    or path.endswith('.pyc')
                    or path.endswith('.pyo')):
                # absolutely no idea how this happens but whenever Flask Unchained
                # gets installed via pip, this cache crap happens
                os.remove(path)
                continue

            root_token = Token()
            try:
                with open(path) as f:
                    lines = f.read().split('\n')
                    root_token, _ = _process_tokens(lines, root_token,
                                                    is_jinja=path.endswith('.html'))
            except UnicodeDecodeError as e:
                raise Exception(f'UnicodeDecodeError: {path} ({str(e)})')

            with open(path, 'w') as f:
                f.write(root_token.render(ctx))


def _process_tokens(lines: List[str],
                    token: Token,
                    *,
                    is_jinja: bool = False,
                    _depth: int = 0,
                    _real_start_i: int = 0):
    start_str = JINJA_START_STR if is_jinja else OTHER_START_STR
    end_str = JINJA_END_STR if is_jinja else None
    i: int = 0
    resume_from_real_i: int = 0
    for i, line in enumerate(lines):
        if (_real_start_i + i) < resume_from_real_i:
            continue

        stripped = line.strip()
        if not stripped.startswith(start_str):
            token.tokens.append(
                _extract_inline_token(line, _real_start_i + i, is_jinja))
            continue

        stripped = stripped[len(start_str):].strip()
        if end_str:
            stripped = right_replace(stripped, end_str, '').strip()

        if stripped == 'endif' and _depth > 0:
            return token, _real_start_i + i

        if_m = IF_RE.match(stripped)
        elif_m = ELIF_RE.match(stripped)
        else_m = ELSE_RE.match(stripped)

        if not any([if_m, elif_m, else_m]) and stripped != 'endif':
            token.tokens.append(InlineToken(_real_start_i + i, [
                line[:line.find(start_str)] + stripped,
            ]))
            continue

        next_start_i = _real_start_i + i + 1
        if if_m is not None:
            condition = if_m.groupdict()['condition']
            statement = if_m.groupdict()['statement']
            if_token = IfToken(_real_start_i + i, condition,
                               line[:line.find(start_str):] + statement
                               if statement else None)
            if not statement:
                if_token, resume_from_real_i = _process_tokens(lines[i + 1:], if_token,
                                                               is_jinja=is_jinja,
                                                               _depth=_depth + 1,
                                                               _real_start_i=next_start_i)
            token.tokens.append(if_token)

        elif elif_m is not None:
            condition = elif_m.groupdict()['condition']
            statement = elif_m.groupdict()['statement']
            if_token = IfToken(_real_start_i + i, condition,
                               line[:line.find(start_str):] + statement
                               if statement else None)
            if not statement:
                if_token, resume_from_real_i = _process_tokens(lines[i + 1:], if_token,
                                                               is_jinja=is_jinja,
                                                               _depth=_depth,
                                                               _real_start_i=next_start_i)
            token.next = if_token

        elif else_m is not None:
            statement = else_m.groupdict()['statement']
            if_token = IfToken(_real_start_i + i, True,
                               line[:line.find(start_str):] + statement
                               if statement else None)
            if not statement:
                if_token, resume_from_real_i = _process_tokens(lines[i + 1:], if_token,
                                                               is_jinja=is_jinja,
                                                               _depth=_depth,
                                                               _real_start_i=next_start_i)
            token.next = if_token
            continue

    return token, _real_start_i + i


def _extract_inline_token(line: str,
                          line_num: int,
                          is_jinja: bool = False):
    start_str = JINJA_START_STR if is_jinja else OTHER_INLINE_START_STR
    end_str = JINJA_END_STR if is_jinja else OTHER_INLINE_END_STR

    if start_str not in line:
        return Token(line_num, line)

    def _clean_end(part):
        if part.startswith(end_str):
            return part[len(end_str):]
        return part

    end_i = 0
    parts = []
    while True:
        start_i = line.find(start_str, end_i)
        if start_i == -1:
            remaining = _clean_end(line[end_i:])
            if remaining:
                parts.append(remaining)
            break

        parts.append(_clean_end(line[end_i:start_i]))
        if is_jinja:
            end_i = line.find(end_str, start_i)
            part = line[start_i+len(start_str):end_i]
        else:
            start_i, end_i = _find_inline_start_end_indexes(line, start_i)
            part = line[start_i:end_i].strip()
        parts.append(InlineToken(line_num, [part]))

    return InlineToken(line_num, parts)


def _find_inline_start_end_indexes(line, start_idx=0):
    s = OTHER_INLINE_START_STR.strip()[-1]
    e = OTHER_INLINE_END_STR
    stack = 0
    last_e = len(line)
    for i, char in enumerate(line[start_idx:]):
        if char == s:
            stack += 1
        elif char == e:
            stack -= 1
            if stack == 0:
                last_e = start_idx + i
                break
    return line.find(s, start_idx) + len(s), last_e
