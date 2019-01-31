"""
This module acts a drop-in replacement for ``click``::

    # before
    import click

    # after
    from flask_unchained import click

We override upstream to do the following:

- we accept ``-h`` and ``--help`` instead of just ``--help`` for showing help
- we support documenting help for ``click.Argument``
- some minor customizations to the formatting of the help output
"""

import click
import inspect as _inspect

from click import *
from click.core import _missing
from click.formatting import join_options as _join_options
from click.utils import make_default_short_help as _make_default_short_help


CLI_HELP_STRING_MAX_LEN = 120
DEFAULT_CONTEXT_SETTINGS = dict(help_option_names=('-h', '--help'))
SKIP_PROMPTING = False


def default(value):
    if SKIP_PROMPTING:
        return AutoDefault(value)
    return value


def skip_prompting(ctx, param, value):
    global SKIP_PROMPTING

    if value:
        SKIP_PROMPTING = True
    else:
        SKIP_PROMPTING = False


class AutoDefault:
    def __init__(self, value):
        self.value = value


def _update_ctx_settings(context_settings):
    rv = DEFAULT_CONTEXT_SETTINGS.copy()
    if not context_settings:
        return rv
    rv.update(context_settings)
    return rv


class Command(click.Command):
    """
    Commands are the basic building block of command line interfaces in
    Click.  A basic command handles command line parsing and might dispatch
    more parsing to commands nested below it.

    :param name: the name of the command to use unless a group overrides it.
    :param context_settings: an optional dictionary with defaults that are
                             passed to the context object.
    :param params: the parameters to register with this command.  This can
                   be either :class:`Option` or :class:`Argument` objects.
    :param help: the help string to use for this command.
    :param epilog: like the help string but it's printed at the end of the
                   help page after everything else.
    :param short_help: the short help to use for this command.  This is
                       shown on the command listing of the parent command.
    :param add_help_option: by default each command registers a ``--help``
                            option.  This can be disabled by this parameter.
    :param options_metavar: The options metavar to display in the usage.
                            Defaults to ``[OPTIONS]``.
    """
    def __init__(self, name, context_settings=None, callback=None, params=None,
                 help=None, epilog=None, short_help=None, add_help_option=True,
                 options_metavar='[OPTIONS]'):
        super().__init__(
            name, callback=callback, params=params, help=help, epilog=epilog,
            short_help=short_help, add_help_option=add_help_option,
            context_settings=_update_ctx_settings(context_settings),
            options_metavar=options_metavar)

    # overridden to support displaying args before the options metavar
    def collect_usage_pieces(self, ctx):
        rv = []
        for param in self.get_params(ctx):
            rv.extend(param.get_usage_pieces(ctx))
        rv.append(self.options_metavar)
        return rv

    # overridden to print arguments first, separately from options
    def format_options(self, ctx, formatter):
        args = []
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if isinstance(param, click.Argument):
                    args.append(rv)
                else:
                    opts.append(rv)
        if args:
            with formatter.section('Arguments'):
                formatter.write_dl(args)
        if opts:
            with formatter.section(self.options_metavar):
                formatter.write_dl(opts)

    # overridden to set the limit parameter to always be CLI_HELP_STRING_MAX_LEN
    def get_short_help_str(self, limit=0):
        if self.short_help:
            return self.short_help
        elif not self.help:
            return ''
        rv = _make_default_short_help(self.help, CLI_HELP_STRING_MAX_LEN)
        return rv


class GroupOverrideMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, context_settings=_update_ctx_settings(
            kwargs.pop('context_settings', None)), **kwargs)
        self.subcommand_metavar = 'COMMAND [<args>...]'
        self.subcommands_metavar = 'COMMAND1 [<args>...] [COMMAND2 [<args>...]]'

    def command(self, *args, **kwargs):
        """
        Commands are the basic building block of command line interfaces in
        Click.  A basic command handles command line parsing and might dispatch
        more parsing to commands nested below it.

        :param name: the name of the command to use unless a group overrides it.
        :param context_settings: an optional dictionary with defaults that are
                                 passed to the context object.
        :param params: the parameters to register with this command.  This can
                       be either :class:`Option` or :class:`Argument` objects.
        :param help: the help string to use for this command.
        :param epilog: like the help string but it's printed at the end of the
                       help page after everything else.
        :param short_help: the short help to use for this command.  This is
                           shown on the command listing of the parent command.
        :param add_help_option: by default each command registers a ``--help``
                                option.  This can be disabled by this parameter.
        :param options_metavar: The options metavar to display in the usage.
                                Defaults to ``[OPTIONS]``.
        :param args_before_options: Whether or not to display the options
                                            metavar before the arguments.
                                            Defaults to False.
        """
        return super().command(
            *args, cls=kwargs.pop('cls', Command) or click.Command, **kwargs)

    def collect_usage_pieces(self, ctx):
        if self.chain:
            rv = [self.subcommands_metavar]
        else:
            rv = [self.subcommand_metavar]
        rv.extend(click.Command.collect_usage_pieces(self, ctx))
        return rv

    # overridden to set the limit parameter to always be CLI_HELP_STRING_MAX_LEN
    def get_short_help_str(self, limit=0):
        if self.short_help:
            return self.short_help
        elif not self.help:
            return ''
        return _make_default_short_help(self.help, CLI_HELP_STRING_MAX_LEN)


class Group(GroupOverrideMixin, click.Group):
    """
    A group allows a command to have subcommands attached.  This is the
    most common way to implement nesting in Click.

    :param name: the name of the group (optional)
    :param commands: a dictionary of commands.
    """

    def group(self, *args, **kwargs):
        """
        A group allows a command to have subcommands attached.  This is the
        most common way to implement nesting in Click.

        :param name: the name of the group (optional)
        :param commands: a dictionary of commands.
        """
        return super().group(
            *args, cls=kwargs.pop('cls', Group) or Group, **kwargs)


class Argument(click.Argument):
    """
    Arguments are positional parameters to a command.  They generally
    provide fewer features than options but can have infinite ``nargs``
    and are required by default.

    :param param_decls: the parameter declarations for this option or
                        argument.  This is a list of flags or argument
                        names.
    :param type: the type that should be used.  Either a :class:`ParamType`
                 or a Python type.  The later is converted into the former
                 automatically if supported.
    :param required: controls if this is optional or not.
    :param default: the default value if omitted.  This can also be a callable,
                    in which case it's invoked when the default is needed
                    without any arguments.
    :param callback: a callback that should be executed after the parameter
                     was matched.  This is called as ``fn(ctx, param,
                     value)`` and needs to return the value.  Before Click
                     2.0, the signature was ``(ctx, value)``.
    :param nargs: the number of arguments to match.  If not ``1`` the return
                  value is a tuple instead of single value.  The default for
                  nargs is ``1`` (except if the type is a tuple, then it's
                  the arity of the tuple).
    :param metavar: how the value is represented in the help page.
    :param expose_value: if this is `True` then the value is passed onwards
                         to the command callback and stored on the context,
                         otherwise it's skipped.
    :param is_eager: eager values are processed before non eager ones.  This
                     should not be set for arguments or it will inverse the
                     order of processing.
    :param envvar: a string or list of strings that are environment variables
                   that should be checked.
    :param help: the help string.
    :param hidden: hide this option from help outputs.
                   Default is True, unless :param:`help` is given.
    """
    def __init__(self, param_decls, required=None, help=None, hidden=None, **attrs):
        super().__init__(param_decls, required=required, **attrs)
        self.help = help
        self.hidden = hidden if hidden is not None else not help

    # overridden to customize the automatic formatting of metavars
    # for example, given self.name = 'query':
    # upstream | (optional) | this-method | (optional)
    # default behavior:
    # QUERY    | [QUERY]    | <query>     | [<query>]
    # when nargs > 1:
    # QUERY... | [QUERY...] | <query>, ... | [<query>, ...]
    def make_metavar(self):
        if self.metavar is not None:
            return self.metavar
        var = '' if self.required else '['
        var += '<' + self.name + '>'
        if self.nargs != 1:
            var += ', ...'
        if not self.required:
            var += ']'
        return var

    # this code is 90% copied from click.Option.get_help_record
    def get_help_record(self, ctx):
        if self.hidden:
            return

        any_prefix_is_slash = []

        def _write_opts(opts):
            rv, any_slashes = _join_options(opts)
            if any_slashes:
                any_prefix_is_slash[:] = [True]
            rv += ': ' + self.make_metavar()
            return rv

        rv = [_write_opts(self.opts)]
        if self.secondary_opts:
            rv.append(_write_opts(self.secondary_opts))

        help = self.help or ''
        extra = []

        if self.default is not None:
            if isinstance(self.default, (list, tuple)):
                default_string = ', '.join('%s' % d for d in self.default)
            elif _inspect.isfunction(self.default):
                default_string = "(dynamic)"
            else:
                default_string = self.default
            extra.append('default: {}'.format(default_string))

        if self.required:
            extra.append('required')
        if extra:
            help = '%s[%s]' % (help and help + '  ' or '', '; '.join(extra))

        return ((any_prefix_is_slash and '; ' or ' / ').join(rv), help)


class Option(click.Option):
    def get_default(self, ctx):
        # If we're a non boolean flag out default is more complex because
        # we need to look at all flags in the same group to figure out
        # if we're the the default one in which case we return the flag
        # value as default.
        if self.is_flag and not self.is_bool_flag:
            for param in ctx.command.params:
                if param.name == self.name and param.default:
                    return param.flag_value
            return None

        # Otherwise go with the regular default.
        if callable(self.default):
            rv = self.default()
        else:
            rv = self.default

        if isinstance(rv, (list, tuple)) and rv[0] is _missing:
            return rv
        return self.type_cast_value(ctx, rv)

    def type_cast_value(self, ctx, value):
        if isinstance(value, AutoDefault):
            return value
        return super().type_cast_value(ctx, value)

    def prompt_for_value(self, ctx):
        """This is an alternative flow that can be activated in the full
        value processing if a value does not exist.  It will prompt the
        user until a valid value exists and then returns the processed
        value as result.
        """
        # Calculate the default before prompting anything to be stable.
        default = self.get_default(ctx)
        if isinstance(default, AutoDefault):
            return self.type_cast_value(ctx, default.value)

        # If this is a prompt for a flag we need to handle this
        # differently.
        if self.is_bool_flag:
            return confirm(self.prompt, default)

        return prompt(self.prompt, default=default,
                      hide_input=self.hide_input,
                      confirmation_prompt=self.confirmation_prompt,
                      value_proc=lambda x: self.process_value(ctx, x))


def command(name=None, cls=None, **attrs):
    """
    Commands are the basic building block of command line interfaces in
    Click.  A basic command handles command line parsing and might dispatch
    more parsing to commands nested below it.

    :param name: the name of the command to use unless a group overrides it.
    :param context_settings: an optional dictionary with defaults that are
                             passed to the context object.
    :param params: the parameters to register with this command.  This can
                   be either :class:`Option` or :class:`Argument` objects.
    :param help: the help string to use for this command.
    :param epilog: like the help string but it's printed at the end of the
                   help page after everything else.
    :param short_help: the short help to use for this command.  This is
                       shown on the command listing of the parent command.
    :param add_help_option: by default each command registers a ``--help``
                            option.  This can be disabled by this parameter.
    :param options_metavar: The options metavar to display in the usage.
                            Defaults to ``[OPTIONS]``.
    :param args_before_options: Whether or not to display the options
                                        metavar before the arguments.
                                        Defaults to False.
    """
    return click.command(name=name, cls=cls or Command, **attrs)


def group(name=None, cls=None, **attrs):
    """
    A group allows a command to have subcommands attached.  This is the
    most common way to implement nesting in Click.

    :param name: the name of the group (optional)
    :param commands: a dictionary of commands.
    :param name: the name of the command to use unless a group overrides it.
    :param context_settings: an optional dictionary with defaults that are
                             passed to the context object.
    :param help: the help string to use for this command.
    :param epilog: like the help string but it's printed at the end of the
                   help page after everything else.
    :param short_help: the short help to use for this command.  This is
                       shown on the command listing of the parent command.
    """
    return click.group(name=name, cls=cls or Group, **attrs)


def argument(*param_decls, cls=None, **attrs):
    """
    Arguments are positional parameters to a command.  They generally
    provide fewer features than options but can have infinite ``nargs``
    and are required by default.

    :param param_decls: the parameter declarations for this option or
                        argument.  This is a list of flags or argument
                        names.
    :param type: the type that should be used.  Either a :class:`ParamType`
                 or a Python type.  The later is converted into the former
                 automatically if supported.
    :param required: controls if this is optional or not.
    :param default: the default value if omitted.  This can also be a callable,
                    in which case it's invoked when the default is needed
                    without any arguments.
    :param callback: a callback that should be executed after the parameter
                     was matched.  This is called as ``fn(ctx, param,
                     value)`` and needs to return the value.  Before Click
                     2.0, the signature was ``(ctx, value)``.
    :param nargs: the number of arguments to match.  If not ``1`` the return
                  value is a tuple instead of single value.  The default for
                  nargs is ``1`` (except if the type is a tuple, then it's
                  the arity of the tuple).
    :param metavar: how the value is represented in the help page.
    :param expose_value: if this is `True` then the value is passed onwards
                         to the command callback and stored on the context,
                         otherwise it's skipped.
    :param is_eager: eager values are processed before non eager ones.  This
                     should not be set for arguments or it will inverse the
                     order of processing.
    :param envvar: a string or list of strings that are environment variables
                   that should be checked.
    :param help: the help string.
    :param hidden: hide this option from help outputs.
                   Default is True, unless help is given.
    """
    return click.argument(*param_decls, cls=cls or Argument, **attrs)


def option(*param_decls, cls=None, **attrs):
    """
    Options are usually optional values on the command line and
    have some extra features that arguments don't have.

    :param param_decls: the parameter declarations for this option or
                        argument.  This is a list of flags or argument
                        names.
    :param show_default: controls if the default value should be shown on the
                         help page.  Normally, defaults are not shown.
    :param prompt: if set to `True` or a non empty string then the user will
                   be prompted for input if not set.  If set to `True` the
                   prompt will be the option name capitalized.
    :param confirmation_prompt: if set then the value will need to be confirmed
                                if it was prompted for.
    :param hide_input: if this is `True` then the input on the prompt will be
                       hidden from the user.  This is useful for password
                       input.
    :param is_flag: forces this option to act as a flag.  The default is
                    auto detection.
    :param flag_value: which value should be used for this flag if it's
                       enabled.  This is set to a boolean automatically if
                       the option string contains a slash to mark two options.
    :param multiple: if this is set to `True` then the argument is accepted
                     multiple times and recorded.  This is similar to ``nargs``
                     in how it works but supports arbitrary number of
                     arguments.
    :param count: this flag makes an option increment an integer.
    :param allow_from_autoenv: if this is enabled then the value of this
                               parameter will be pulled from an environment
                               variable in case a prefix is defined on the
                               context.
    :param help: the help string.
    """
    return click.option(*param_decls, cls=cls or Option, **attrs)
