from flask_unchained.commands.new import Token, _process_tokens


CTX = dict(fooFalse=False, fooTrue=True, fooTrueToo=True, else_='else!',
           foo_true_too='fooTrueToo!', foo_true_moo='fooTrueMoo!',
           regular_comment='regular comment',
           security=False, session=True, sqlalchemy=False)


SIMPLE = """
one
two
#! if fooFalse:
    fooFalse!
#! else:
    inline >#!({{ else_ }})< ya
#! endif
#! if security or session:
    #! SESSION_TYPE = "{{ 'sqlalchemy' if sqlalchemy else 'filesystem' }}"
#! endif
last
"""


SIMPLE_EXPECTED = """
one
two
    inline >else!< ya
    SESSION_TYPE = "filesystem"
last
"""

NESTED = """
one
two
#! if fooFalse:
    fooFalse!
#! else:
    inline >#!( {{ else_ }} )< ya
#! endif
#! if fooTrue:
    fooTrueOne!
    #! if fooFalse:
        fooFalse!
    #! elif fooTrueToo:
        inline >#!({{ foo_true_too }})< ya >#!({{ foo_true_moo }})< yup
    #! else:
        nestedElse!
    #! endif
    fooTrueTwo!
#! endif
last
"""


NESTED_EXPECTED = """
one
two
    inline >else!< ya
    fooTrueOne!
        inline >fooTrueToo!< ya >fooTrueMoo!< yup
    fooTrueTwo!
last
"""


JINJA = """
{% extends 'whatever.html' %}

{# {{ regular_comment }} #}
{#! not a {{ regular_comment }} #}
{#! if fooFalse: #}
    fooFalse!
{#! else: #}
    {#! {{ else_ }} #}
{#! endif #}
last
"""


JINJA_EXPECTED = """
{% extends 'whatever.html' %}

{# {{ regular_comment }} #}
not a regular comment
    else!
last
"""


class TestGenerateCommand:
    def test_process_tokens(self):
        root_token = Token()
        root_token, _ = _process_tokens(SIMPLE.split('\n'), root_token)
        assert root_token.render(CTX) == SIMPLE_EXPECTED

    def test_process_tokens_nested(self):
        root_token = Token()
        root_token, _ = _process_tokens(NESTED.split('\n'), root_token)
        assert root_token.render(CTX) == NESTED_EXPECTED

    def test_process_tokens_jinja(self):
        root_token = Token()
        root_token, _ = _process_tokens(JINJA.split('\n'), root_token, is_jinja=True)
        assert root_token.render(CTX) == JINJA_EXPECTED
