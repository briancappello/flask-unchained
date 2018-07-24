import pytest

from flask_unchained.bundles.sqlalchemy.meta.model_registry import _model_registry
from tests.conftest import POSTGRES


class TestModelMetaOptions:
    def test_defaults(self, db):
        meta = db.Model._meta
        assert meta._testing_ == 'this setting is only available when ' \
                                 'os.getenv("FLASK_ENV") == "test"'

        assert meta.abstract is True
        assert meta.lazy_mapped is False
        assert meta.relationships is None

        assert meta._base_tablename is None
        assert meta.polymorphic is False
        assert meta.polymorphic_on is None
        assert meta.polymorphic_identity is None

        assert meta.pk == 'id'
        assert meta.created_at == 'created_at'
        assert meta.updated_at == 'updated_at'

    def test_overriding_defaults_with_inheritance(self, db):
        class Over(db.Model):
            class Meta:
                relationships = {}
                pk = 'pk'
                created_at = 'created'
                updated_at = 'updated'
                _testing_ = 'over'

        meta = Over._meta
        assert meta._testing_ == 'over'
        assert meta.abstract is False
        assert meta.lazy_mapped is False
        assert meta.relationships == {}

        assert meta._base_tablename is None
        assert meta.polymorphic is False
        assert meta.polymorphic_on is None
        assert meta.polymorphic_identity is None

        assert meta.pk == 'pk'
        assert meta.created_at == 'created'
        assert meta.updated_at == 'updated'

        class ExtendsOver(Over):
            class Meta:
                lazy_mapped = True
                updated_at = 'extends'

        meta = ExtendsOver._meta
        assert meta._testing_ == 'over'
        assert meta.abstract is False
        assert meta.lazy_mapped is True
        assert meta.relationships == {}

        assert meta._base_tablename == 'over'
        assert meta.polymorphic is False
        assert meta.polymorphic_on is None
        assert meta.polymorphic_identity is None

        assert meta.pk == 'pk'
        assert meta.created_at == 'created'
        assert meta.updated_at == 'extends'

    def test_abstract(self, db):
        class Classic(db.Model):
            __abstract__ = True

        _model_registry.finalize_mappings()
        assert Classic._meta.abstract is True
        assert Classic._meta._mcs_args.clsdict['__abstract__'] is True

        class MyMeta(db.Model):
            class Meta:
                abstract = True

        _model_registry.finalize_mappings()
        assert MyMeta._meta.abstract is True
        assert MyMeta._meta._mcs_args.clsdict['__abstract__'] is True

    def test_primary_key(self, db):
        class NotLazy(db.Model):
            class Meta:
                abstract = True
                lazy_mapped = False

        class DoesntOverwrite(NotLazy):
            id = 'not a column'
            a_pk_is_still_required = db.Column(db.Integer, primary_key=True)

        assert DoesntOverwrite.id == 'not a column'

        class Manual(NotLazy):
            class Meta:
                pk = None
            pk = db.Column(db.Integer, primary_key=True)

        assert not hasattr(Manual, 'id')

        class Auto(NotLazy):
            pass

        assert Auto.id.primary_key is True

        class Renamed(NotLazy):
            class Meta:
                pk = 'pk'

        assert not hasattr(Renamed, 'id')
        assert Renamed.pk.primary_key is True

    def test_polymorphic_auto_base_tablename(self, db):
        class Base(db.Model):
            class Meta:
                lazy_mapped = False
                polymorphic = True

        class YellowSubmarine(Base):
            pass

        class GlassOnion(YellowSubmarine):
            pass

        assert Base._meta._base_tablename is None
        assert YellowSubmarine._meta._base_tablename == 'base'
        assert GlassOnion._meta._base_tablename == 'yellow_submarine'

    def test_polymorphic_manual_base_tablename(self, db):
        class Base(db.Model):
            class Meta:
                lazy_mapped = False
                polymorphic = True
                table = 'bases'

        class YellowSubmarine(Base):
            class Meta:
                table = 'yellow_subs'

        class GlassOnion(YellowSubmarine):
            pass

        assert Base._meta._base_tablename is None
        assert YellowSubmarine._meta._base_tablename == 'bases'
        assert GlassOnion._meta._base_tablename == 'yellow_subs'

    def test_polymorphic_manual_declared_attr_tablename(self, db):
        class Base(db.Model):
            class Meta:
                lazy_mapped = False
                polymorphic = True

            @db.declared_attr
            def __tablename__(cls):
                return cls.__name__.lower() + 's'

        class YellowSubmarine(Base):
            id = db.foreign_key(Base.__tablename__, primary_key=True)

        class GlassOnion(YellowSubmarine):
            id = db.foreign_key(YellowSubmarine.__tablename__, primary_key=True)

        assert Base._meta._base_tablename is None
        assert Base.__tablename__ == 'bases'
        assert YellowSubmarine._meta._base_tablename is None
        assert YellowSubmarine.__tablename__ == 'yellowsubmarines'
        assert GlassOnion._meta._base_tablename is None

    def test_polymorphic_declared_attr_tablename(self, db):
        class Base(db.Model):
            class Meta:
                lazy_mapped = False
                polymorphic = True

            @db.declared_attr
            def __tablename__(cls):
                return cls.__name__.lower() + 's'

        class YellowSubmarine(Base):
            pass

        class GlassOnion(YellowSubmarine):
            pass

        assert Base._meta._base_tablename is None
        assert Base.__tablename__ == 'bases'
        assert YellowSubmarine._meta._base_tablename is None
        assert YellowSubmarine.__tablename__ == 'yellowsubmarines'
        assert GlassOnion._meta._base_tablename is None

    @pytest.mark.options(SQLALCHEMY_DATABASE_URI=POSTGRES)
    def test_tablename(self, db):
        class NotLazy(db.Model):
            class Meta:
                abstract = True
                lazy_mapped = False

        class Auto(NotLazy):
            pass

        assert Auto._meta.table is None
        assert '__tablename__' not in Auto._meta._mcs_args.clsdict
        assert Auto.__tablename__ == 'auto'

        class DeclaredAttr(NotLazy):
            @db.declared_attr
            def __tablename__(cls):
                return cls.__name__.lower()

        assert DeclaredAttr._meta.table is None
        assert DeclaredAttr.__tablename__ == 'declaredattr'

        class Manual(NotLazy):
            __tablename__ = 'manuals'

        assert Manual._meta.table == 'manuals'
        assert Manual._meta._mcs_args.clsdict['__tablename__'] == 'manuals'
        assert Manual.__tablename__ == 'manuals'

        class AutoMV(db.MaterializedView):
            @classmethod
            def selectable(cls):
                return db.select([Auto.id])

        _model_registry.finalize_mappings()

        assert AutoMV._meta.table == 'auto_mv'
        assert AutoMV.__table__.fullname == 'auto_mv'
        assert AutoMV._meta._mcs_args.clsdict['__tablename__'] == 'auto_mv'
        assert AutoMV.__tablename__ == 'auto_mv'

        class ManualMV(db.MaterializedView):
            class Meta:
                table = 'manual_materialized_view'

            @classmethod
            def selectable(cls):
                return db.select([Manual.id])

        _model_registry.finalize_mappings()

        assert ManualMV._meta.table == 'manual_materialized_view'
        assert ManualMV.__table__.fullname == 'manual_materialized_view'
        assert ManualMV._meta._mcs_args.clsdict['__tablename__'] == \
               'manual_materialized_view'
        assert ManualMV.__tablename__ == 'manual_materialized_view'
