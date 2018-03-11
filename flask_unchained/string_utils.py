import re
import unicodedata

# alias these to the string_utils module
from .clips_pattern import de_camel, pluralize, singularize


def camel_case(string):
    if not string:
        return string
    parts = snake_case(string).split('_')
    return parts[0] + ''.join(x.title() for x in parts[1:])


def class_case(string):
    return title_case(string).replace(' ', '')


def kebab_case(string):
    if not string:
        return string
    string = string.replace('_', '-').replace(' ', '-')
    return de_camel(string, '-').strip('-')


def right_replace(string, old, new, count=1):
    if not string:
        return string
    return new.join(string.rsplit(old, count))


def slugify(string):
    if not string:
        return string

    string = re.sub(r'[^\w\s-]', '',
                    unicodedata.normalize('NFKD', string)
                    .encode('ascii', 'ignore')
                    .decode('ascii')).strip()

    return re.sub(r'[-\s]+', '-', string).lower()


def snake_case(string):
    if not string:
        return string
    string = string.replace('-', '_').replace(' ', '_')
    return de_camel(string)


def title_case(string):
    if not string:
        return string
    string = string.replace('_', ' ').replace('-', ' ')
    return de_camel(string, ' ').title().strip()
