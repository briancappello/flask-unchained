import pytest

from flask_unchained.hooks.run_hooks_hook import HookTuple, RunHooksHook
from flask_unchained import unchained


@pytest.fixture()
def hook():
    return RunHooksHook(unchained)


def make_hook_tuple(name, run_after=None, run_before=None):
    HookCls = type(name.title(), (), dict(name=name,
                                          run_after=run_after or [],
                                          run_before=run_before or []))
    return HookTuple(HookCls, None)


def test_resolve_hook_order_fully_specified(hook: RunHooksHook):
    one = make_hook_tuple('one', run_before=['two', 'three'])
    two = make_hook_tuple('two', run_after=['one'], run_before=['three'])
    three = make_hook_tuple('three', run_after=['one', 'two'])

    result = hook.resolve_hook_order({'Three': three, 'Two': two, 'One': one})
    assert result == [one, two, three]


def test_resolve_hook_order_only_run_after(hook: RunHooksHook):
    one = make_hook_tuple('one')
    two = make_hook_tuple('two', run_after=['one'])
    three = make_hook_tuple('three', run_after=['one', 'two'])

    result = hook.resolve_hook_order({'Three': three, 'Two': two, 'One': one})
    assert result == [one, two, three]


def test_resolve_hook_order_only_run_before(hook: RunHooksHook):
    one = make_hook_tuple('one', run_before=['two', 'three'])
    two = make_hook_tuple('two', run_before=['three'])
    three = make_hook_tuple('three')

    result = hook.resolve_hook_order({'Two': two, 'One': one, 'Three': three})
    assert result == [one, two, three]


def test_resolve_hook_order_optional_run_after(hook: RunHooksHook):
    one = make_hook_tuple('one', run_before=['two', 'three'])
    two = make_hook_tuple('two', run_before=['three'])
    three = make_hook_tuple('three', run_after=['one_half'])

    result = hook.resolve_hook_order({'Two': two, 'Three': three, 'One': one})
    assert result == [one, two, three]


def test_resolve_hook_order_optional_run_before(hook: RunHooksHook):
    one = make_hook_tuple('one', run_before=['four'])
    two = make_hook_tuple('two', run_after=['one'])
    three = make_hook_tuple('three', run_after=['one', 'two'])

    result = hook.resolve_hook_order({'Three': three, 'Two': two, 'One': one})
    assert result == [one, two, three]
