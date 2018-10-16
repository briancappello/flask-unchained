import pytest

from flask_unchained import unchained
from werkzeug.local import LocalProxy

from tests.bundles.sqlalchemy._bundles.custom_extension.extensions import (
    SQLAlchemyUnchained as CustomSQLAlchemy,
    Model as CustomModel)


@pytest.mark.bundles(['tests.bundles.sqlalchemy._bundles.custom_extension',
                      'tests.bundles.sqlalchemy._bundles.ext_vendor_one',
                      'tests.bundles.sqlalchemy._bundles.vendor_two'])
@pytest.mark.usefixtures('app', 'db')
class TestCustomExtension:
    def test_it_works(self, app, db):
        exts = [db, app.extensions['sqlalchemy'].db, unchained.extensions.db]
        for i, ext in enumerate(exts):
            if isinstance(ext, LocalProxy):
                ext = ext._get_current_object()
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
        assert db.Model.Meta.extend_existing is True
        assert db.Model.Meta.pk == 'pk'
        assert db.Model.Meta._testing_ == 'overriding the default'

        assert db.MaterializedView.Meta.pk is None
        assert db.MaterializedView.Meta.created_at is None
        assert db.MaterializedView.Meta.updated_at is None
        assert db.Model.Meta._testing_ == 'overriding the default'
