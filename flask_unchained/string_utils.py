import re
import unicodedata

# alias these to the string_utils module
from .clips_pattern import de_camel, pluralize, singularize


def camel_case(string):
    """
    Converts a string to camel case. For example::

        camel_case('one_two_three') -> 'oneTwoThree'
    """
    if not string:
        return string
    parts = snake_case(string).split('_')
    rv = ''
    while parts:
        part = parts.pop(0)
        rv += part or '_'
        if part:
            break
    return rv + ''.join(x.title() for x in parts)


def class_case(string):
    """
    Converts a string to class case. For example::

        class_case('one_two_three') -> 'OneTwoThree'
    """
    if not string:
        return string
    string = string.replace(' ', '_').replace('-', '_')
    parts = de_camel(string, '_', _lowercase=False).split('_')
    rv = ''
    while parts:
        part = parts.pop(0)
        rv += part.title() or '_'
        if part:
            break
    return rv + ''.join([part if part.isupper() else part.title()
                         for part in parts])


def kebab_case(string):
    """
    Converts a string to kebab case. For example::

        kebab_case('one_two_three') -> 'one-two-three'

    NOTE: To generate valid slugs, use :meth:`slugify`
    """
    if not string:
        return string
    string = string.replace('_', '-').replace(' ', '-')
    return de_camel(string, '-')


def right_replace(string, old, new, count=1):
    """
    Right replaces ``count`` occurrences of ``old`` with ``new`` in ``string``.
    For example::

        right_replace('one_two_two', 'two', 'three') -> 'one_two_three'
    """
    if not string:
        return string
    return new.join(string.rsplit(old, count))


def slugify(string):
    """
    Converts a string to a valid slug. For example::

        slugify('Hello World') -> 'hello-world'
    """
    if not string:
        return string
    string = re.sub(r'[^\w\s-]', '',
                    unicodedata.normalize('NFKD', de_camel(string, '-'))
                    .encode('ascii', 'ignore')
                    .decode('ascii')).strip()
    return re.sub(r'[-_\s]+', '-', string).strip('-').lower()


def snake_case(string):
    """
    Converts a string to snake case. For example::

        snake_case('OneTwoThree') -> 'one_two_three'
    """
    if not string:
        return string
    string = string.replace('-', '_').replace(' ', '_')
    return de_camel(string)


def title_case(string):
    """
    Converts a string to title case. For example::

        title_case('one_two_three') -> 'One Two Three'
    """
    if not string:
        return string
    string = string.replace('_', ' ').replace('-', ' ')
    parts = de_camel(string, ' ', _lowercase=False).strip().split(' ')
    return ' '.join([part if part.isupper() else part.title()
                     for part in parts])
