import re
import unicodedata

# alias these to the string_utils module
from .clips_pattern import de_camel, pluralize, singularize


def camel_case(string):
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
    if not string:
        return string
    string = string.replace('_', '-').replace(' ', '-')
    return de_camel(string, '-')


def right_replace(string, old, new, count=1):
    if not string:
        return string
    return new.join(string.rsplit(old, count))


def slugify(string):
    if not string:
        return string
    string = re.sub(r'[^\w\s-]', '',
                    unicodedata.normalize('NFKD', de_camel(string, '-'))
                    .encode('ascii', 'ignore')
                    .decode('ascii')).strip()
    return re.sub(r'[-_\s]+', '-', string).strip('-').lower()


def snake_case(string):
    if not string:
        return string
    string = string.replace('-', '_').replace(' ', '_')
    return de_camel(string)


def title_case(string):
    if not string:
        return string
    string = string.replace('_', ' ').replace('-', ' ')
    parts = de_camel(string, ' ', _lowercase=False).strip().split(' ')
    return ' '.join([part if part.isupper() else part.title()
                     for part in parts])
