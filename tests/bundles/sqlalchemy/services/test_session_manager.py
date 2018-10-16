from flask_unchained.bundles.sqlalchemy import SessionManager, SQLAlchemyUnchained


def setup(db: SQLAlchemyUnchained):
    session_manager = SessionManager(db)

    class Foo(db.Model):
        class Meta:
            lazy_mapped = False

        name = db.Column(db.String)

    db.create_all()
    return Foo, session_manager


class TestSessionManager:
    def test_save(self, db: SQLAlchemyUnchained):
        Foo, session_manager = setup(db)

        foo = Foo(name='foo')
        session_manager.save(foo)

        # check it's added to the session but not committed
        assert foo in db.session
        with db.session.no_autoflush:
            assert Foo.q.get_by(name='foo') is None

        # check the commit kwarg works
        session_manager.save(foo, commit=True)
        assert Foo.q.get_by(name='foo') == foo

    def test_save_all(self, db: SQLAlchemyUnchained):
        Foo, session_manager = setup(db)

        foo1 = Foo(name='one')
        foo2 = Foo(name='two')
        foo3 = Foo(name='three')
        all_ = [foo1, foo2, foo3]

        session_manager.save_all(all_)
        with db.session.no_autoflush:
            for foo in all_:
                assert foo in db.session
                assert Foo.q.get_by(name=foo.name) is None

        session_manager.save_all(all_, commit=True)
        for foo in all_:
            assert Foo.q.get_by(name=foo.name) == foo

    def test_delete(self, db: SQLAlchemyUnchained):
        Foo, session_manager = setup(db)

        foo1 = Foo(name='one')
        foo2 = Foo(name='two')
        all_ = [foo1, foo2]
        session_manager.save_all(all_, commit=True)

        for foo in all_:
            assert foo in db.session
            assert Foo.q.get_by(name=foo.name) == foo

        session_manager.delete(foo1, commit=True)
        assert foo1 not in db.session
        assert Foo.q.get_by(name='one') is None
        assert foo2 in db.session
        assert Foo.q.get_by(name='two') == foo2
