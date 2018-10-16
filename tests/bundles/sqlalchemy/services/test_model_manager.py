import pytest

from flask_unchained.bundles.sqlalchemy import ModelManager, SQLAlchemyUnchained
from flask_unchained.bundles.sqlalchemy.model_registry import UnchainedModelRegistry
from flask_unchained import unchained
from sqlalchemy.orm.exc import MultipleResultsFound


def setup(db: SQLAlchemyUnchained):
    class Foo(db.Model):
        name = db.Column(db.String)

    # simulate the register models hook
    unchained.sqlalchemy_bundle.models['Foo'] = Foo

    class FooManager(ModelManager):
        class Meta:
            model = Foo

    UnchainedModelRegistry().finalize_mappings()
    db.create_all()

    return Foo, FooManager()


class TestModelManager:
    def test_it_accepts_a_model_class(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo = foo_manager.create(name='foobar')
        assert isinstance(foo, Foo)

        # check it's added to the session but not committed
        assert foo in db.session
        with db.session.no_autoflush:
            assert foo_manager.get_by(name='foobar') is None

        foo_manager.commit()
        assert foo_manager.get_by(name='foobar') == foo

    def test_it_accepts_a_model_class_by_name(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo = foo_manager.create(name='foobar')
        assert isinstance(foo, Foo)

        # check it's added to the session but not committed
        assert foo in db.session
        with db.session.no_autoflush:
            assert foo_manager.get_by(name='foobar') is None

        foo_manager.commit()
        assert foo_manager.get_by(name='foobar') == foo

    def test_update(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo = foo_manager.create(name='foo')
        foo_manager.commit()

        foo_manager.update(foo, name='foobar')
        foo_manager.commit()

        assert foo_manager.get_by(name='foobar') == foo

    def test_get(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo = foo_manager.create(name='foo')
        foo_manager.commit()

        assert foo_manager.get(int(foo.id)) == foo
        assert foo_manager.get(float(foo.id)) == foo
        assert foo_manager.get(str(foo.id)) == foo

        assert foo_manager.get(42) is None

    def test_get_or_create(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo, created = foo_manager.get_or_create(name='foo')
        assert created is True
        assert foo in db.session
        with db.session.no_autoflush:
            assert foo_manager.get_by(name='foo') is None
        foo_manager.commit()
        assert foo_manager.get_by(name='foo') == foo

        foo1, created = foo_manager.get_or_create(id=foo.id)
        assert created is False
        assert foo1 == foo

        foo1, created = foo_manager.get_or_create(name='foo')
        assert created is False
        assert foo1 == foo

        foo2, created = foo_manager.get_or_create(name='foobar')
        assert created is True

    def test_get_by(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo1 = foo_manager.create(name='one')
        foo_1 = foo_manager.create(name='one')
        foo2 = foo_manager.create(name='two')
        foo_manager.commit()

        assert foo_manager.get_by(name='fail') is None
        with pytest.raises(MultipleResultsFound):
            foo_manager.get_by(name='one')

        assert foo_manager.get_by(name='two') == foo2

    def test_find_all(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo1 = foo_manager.create(name='one')
        foo2 = foo_manager.create(name='two')
        foo3 = foo_manager.create(name='three')
        foo_manager.commit()

        all_ = [foo1, foo2, foo3]
        assert foo_manager.all() == all_

    def test_find_by(self, db: SQLAlchemyUnchained):
        Foo, foo_manager = setup(db)

        foo1 = foo_manager.create(name='one')
        foo_1 = foo_manager.create(name='one')
        foo2 = foo_manager.create(name='two')
        foo_manager.commit()

        ones = [foo1, foo_1]
        assert foo_manager.filter_by(name='one') == ones
