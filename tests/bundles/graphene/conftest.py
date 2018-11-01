import pytest

from flask_unchained import unchained
from flask_unchained.bundles.graphene.pytest import *
from ..sqlalchemy.conftest import *


parent_manager = unchained.get_local_proxy('parent_manager')
child_manager = unchained.get_local_proxy('child_manager')
session_manager = unchained.get_local_proxy('session_manager')


@pytest.fixture(autouse=True)
def parents():
    parent_one = parent_manager.create(name='parent_one')
    child_one = child_manager.create(name='child_one', parent=parent_one)
    child_two = child_manager.create(name='child_two', parent=parent_one)

    parent_two = parent_manager.create(name='parent_two')
    child_three = child_manager.create(name='child_three', parent=parent_two)
    child_four = child_manager.create(name='child_four', parent=parent_two)

    session_manager.commit()
    yield [parent_one, parent_two]
