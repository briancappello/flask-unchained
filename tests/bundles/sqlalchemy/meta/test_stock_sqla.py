import pytest


class TestStockSQLA:
    def test_abstract_set_by_attr_or_by_meta_option(self, db):
        class AbstractAttr(db.Model):
            __abstract__ = True

        assert AbstractAttr._meta.abstract is True
        assert '__abstract__' in AbstractAttr._meta._mcs_args.clsdict

        class AbstractMeta(db.Model):
            class Meta:
                abstract = True

        assert AbstractMeta._meta.abstract is True
        assert '__abstract__' in AbstractMeta._meta._mcs_args.clsdict

    def test_columns_do_not_override_existing_attributes(self, db):
        class Columns(db.Model):
            _ = db.Column(db.Integer, primary_key=True)

            class Meta:
                pk = 'id'
                created_at = 'created_at'
                updated_at = 'updated_at'

            id = 'not a column'
            created_at = 'not a column'
            updated_at = 'not a column'

        assert Columns.id == 'not a column'
        assert Columns.created_at == 'not a column'
        assert Columns.updated_at == 'not a column'

    def test_manual_polymorphic_models(self, db):
        class Person(db.Model):
            type = db.Column(db.String)
            __mapper_args__ = {'polymorphic_on': type,
                               'polymorphic_identity': 'base person'}

        # there's no way to know whether user wants single, joined, or concrete
        # so most polymorphic magic must remain disabled
        assert Person._meta.polymorphic == '_manual_'
        assert not hasattr(Person, 'discriminator')
        assert Person._meta.polymorphic_on is None
        assert Person._meta.polymorphic_identity == 'base person'

        class Employee(Person):
            __table_args__ = None

        assert Employee.id == Person.id
        assert Employee._meta.polymorphic_identity == 'Employee'

    def test_declared_attr_polymorphic_models(self, db):
        class Person(db.Model):
            type = db.Column(db.String)

            @db.declared_attr
            def __mapper_args__(cls):
                if cls.__name__ == 'Person':
                    return {'polymorphic_on': cls.type,
                            'polymorphic_identity': cls.__name__}
                else:
                    return {'polymorphic_identity': cls.__name__}

        # when the user has used a @declared_attr for __mapper_args__, there's
        # no way to know anything, so all polymorphic magic must be disabled
        assert Person._meta.polymorphic == '_fully_manual_'
        assert not hasattr(Person, 'discriminator')
        assert Person._meta.polymorphic_on is None
        assert Person._meta.polymorphic_identity is None

        class Employee(Person):
            __table_args__ = None

        assert Employee.id == Person.id
        assert Employee._meta.polymorphic_identity is None
