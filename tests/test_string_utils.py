from flask_unchained.string_utils import (camel_case, class_case, kebab_case,
                                          right_replace, slugify, snake_case,
                                          title_case)


def test_camel_case():
    assert camel_case('aCamelCasedString') == 'aCamelCasedString'
    assert camel_case('A_snake_cased_string') == 'aSnakeCasedString'
    assert camel_case('A-kebab-cased-string') == 'aKebabCasedString'
    assert camel_case('A normal sentence') == 'aNormalSentence'
    assert camel_case('_an underscore-prefix') == '_anUnderscorePrefix'
    assert camel_case('__a private-prefix') == '__aPrivatePrefix'
    assert camel_case('FoobarAPIController') == 'foobarApiController'
    assert camel_case('') == ''
    assert camel_case(None) is None


def test_class_case():
    assert class_case('aCamelCasedString') == 'ACamelCasedString'
    assert class_case('A_snake_cased_string') == 'ASnakeCasedString'
    assert class_case('A-kebab-cased-string') == 'AKebabCasedString'
    assert class_case('A normal sentence') == 'ANormalSentence'
    assert class_case('_an underscore-prefix') == '_AnUnderscorePrefix'
    assert class_case('__a private-prefix') == '__APrivatePrefix'
    assert class_case('FoobarAPIController') == 'FoobarAPIController'
    assert class_case('') == ''
    assert class_case(None) is None


def test_right_replace():
    assert right_replace('aabb', 'b', 'c') == 'aabc'
    assert right_replace('aabbcc', 'b', 'd') == 'aabdcc'
    assert right_replace('abaa', 'a', 'c', count=2) == 'abcc'
    assert right_replace('abaa', 'a', 'c', count=3) == 'cbcc'
    assert right_replace('abaa', 'a', 'c', count=4) == 'cbcc'
    assert right_replace('abc', 'd', 'e') == 'abc'
    assert right_replace('', 'a', 'b') == ''
    assert right_replace(None, 'a', 'b') is None


def test_kebab_case():
    assert kebab_case('aCamelCasedString') == 'a-camel-cased-string'
    assert kebab_case('A_snake_cased_string') == 'a-snake-cased-string'
    assert kebab_case('A-kebab-cased-string') == 'a-kebab-cased-string'
    assert kebab_case('A normal sentence') == 'a-normal-sentence'
    assert kebab_case('_an underscore-prefix') == '-an-underscore-prefix'
    assert kebab_case('__a private-prefix') == '--a-private-prefix'
    assert kebab_case('FoobarAPIController') == 'foobar-api-controller'
    assert kebab_case('') == ''
    assert kebab_case(None) is None


def test_slugify():
    assert slugify('aCamelCasedString') == 'a-camel-cased-string'
    assert slugify('A_snake_cased_string') == 'a-snake-cased-string'
    assert slugify('A-kebab-cased-string') == 'a-kebab-cased-string'
    assert slugify('A normal sentence') == 'a-normal-sentence'
    assert slugify('multiple   spaces') == 'multiple-spaces'
    assert slugify('multiple---dashes') == 'multiple-dashes'
    assert slugify('Héllö Wørld') == 'hello-wrld'  # unicode-to-ascii is so-so
    assert slugify('_an underscore-prefix') == 'an-underscore-prefix'
    assert slugify('FoobarAPIController') == 'foobar-api-controller'
    assert slugify('') == ''
    assert slugify(None) is None


def test_snake_case():
    assert snake_case('aCamelCasedString') == 'a_camel_cased_string'
    assert snake_case('A_snake_cased_string') == 'a_snake_cased_string'
    assert snake_case('A-kebab-cased-string') == 'a_kebab_cased_string'
    assert snake_case('A normal sentence') == 'a_normal_sentence'
    assert snake_case('_an underscore-prefix') == '_an_underscore_prefix'
    assert snake_case('__a private-prefix') == '__a_private_prefix'
    assert snake_case('FoobarAPIController') == 'foobar_api_controller'
    assert snake_case('') == ''
    assert snake_case(None) is None


def test_title_case():
    assert title_case('aCamelCasedString') == 'A Camel Cased String'
    assert title_case('A_snake_cased_string') == 'A Snake Cased String'
    assert title_case('A-kebab-cased-string') == 'A Kebab Cased String'
    assert title_case('A normal sentence') == 'A Normal Sentence'
    assert title_case('_an underscore-prefix') == 'An Underscore Prefix'
    assert title_case('FoobarAPIController') == 'Foobar API Controller'
    assert title_case('') == ''
    assert title_case(None) is None
