from flask_unchained.bundles.sqlalchemy import db
from flask_unchained.bundles.sqlalchemy.sqla.foreign_key import foreign_key


def test_it_works_with_a_class():
    class FakeModel(db.Model):
        __tablename__ = 'custom_tablename'
    col = foreign_key(FakeModel)
    assert col.name is None
    assert list(col.foreign_keys)[0]._get_colspec() == 'custom_tablename.id'

    col = foreign_key(FakeModel, fk_col='pk')
    assert col.name is None
    assert list(col.foreign_keys)[0]._get_colspec() == 'custom_tablename.pk'

    col = foreign_key('custom_column', FakeModel)
    assert col.name == 'custom_column'
    assert list(col.foreign_keys)[0]._get_colspec() == 'custom_tablename.id'

    col = foreign_key('custom_column', FakeModel, fk_col='pk')
    assert col.name == 'custom_column'
    assert list(col.foreign_keys)[0]._get_colspec() == 'custom_tablename.pk'


def test_it_works_with_a_class_name():
    col = foreign_key('ClassName')
    assert col.name is None
    assert list(col.foreign_keys)[0]._get_colspec() == 'class_name.id'

    col = foreign_key('ClassName', fk_col='pk')
    assert col.name is None
    assert list(col.foreign_keys)[0]._get_colspec() == 'class_name.pk'

    col = foreign_key('custom_column', 'ClassName')
    assert col.name == 'custom_column'
    assert list(col.foreign_keys)[0]._get_colspec() == 'class_name.id'

    col = foreign_key('custom_column', 'ClassName', fk_col='pk')
    assert col.name == 'custom_column'
    assert list(col.foreign_keys)[0]._get_colspec() == 'class_name.pk'


def test_it_works_with_a_table_name():
    col = foreign_key('a_table_name')
    assert col.name is None
    assert list(col.foreign_keys)[0]._get_colspec() == 'a_table_name.id'

    col = foreign_key('a_table_name', fk_col='pk')
    assert col.name is None
    assert list(col.foreign_keys)[0]._get_colspec() == 'a_table_name.pk'

    col = foreign_key('custom_column', 'a_table_name')
    assert col.name == 'custom_column'
    assert list(col.foreign_keys)[0]._get_colspec() == 'a_table_name.id'

    col = foreign_key('custom_column', 'a_table_name', fk_col='pk')
    assert col.name == 'custom_column'
    assert list(col.foreign_keys)[0]._get_colspec() == 'a_table_name.pk'
