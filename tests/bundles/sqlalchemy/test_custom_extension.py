import pytest

from flask_unchained import unchained

from tests.bundles.sqlalchemy._bundles.custom_extension.extensions import (
    SQLAlchemy as CustomSQLAlchemy,
    Model as CustomModel)


@pytest.mark.bundles(['tests.bundles.sqlalchemy._bundles.custom_extension',
                      'tests.bundles.sqlalchemy._bundles.ext_vendor_one',
                      'tests.bundles.sqlalchemy._bundles.vendor_two'])
@pytest.mark.usefixtures('app', 'db')
class TestCustomExtension:
    def test_it_works(self, app, db):
        exts = [db, app.extensions['sqlalchemy'].db, unchained.extensions.db]
        for i, ext in enumerate(exts):
            assert isinstance(ext, CustomSQLAlchemy), i
            assert ext == db, i

    def test_it_uses_the_correct_base_model(self, db):
        assert issubclass(db.Model, CustomModel)
        assert issubclass(db.MaterializedView, CustomModel)

        from ._bundles.ext_vendor_one.models import OneBasic, OneRole
        assert issubclass(OneBasic, CustomModel)
        assert issubclass(OneRole, CustomModel)

        from ._bundles.vendor_two.models import TwoBasic
        assert issubclass(TwoBasic, CustomModel)

    def test_base_model_meta_options_are_correct(self, db):
        assert db.Model._meta.extend_existing is True
        assert db.Model._meta.pk == 'pk'
        assert db.Model._meta._testing_ == 'overriding the default'

        assert db.MaterializedView._meta.pk is None
        assert db.MaterializedView._meta.created_at is None
        assert db.MaterializedView._meta.updated_at is None
        assert db.Model._meta._testing_ == 'overriding the default'
