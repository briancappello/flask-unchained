from sqlalchemy_unchained.foreign_key import _get_fk_col_args
from typing import *

from .column import Column
from .types import BigInteger


def foreign_key(*args,
                fk_col: Optional[str] = None,
                primary_key: bool = False,
                nullable: bool = False,
                **kwargs,
                ) -> Column:
    """
    Helper method to add a foreign key column to a model.

    For example::

        class Post(db.Model):
            category_id = db.foreign_key('Category')
            category = db.relationship('Category', back_populates='posts')

    Is equivalent to::

        class Post(db.Model):
            category_id = db.Column(db.BigInteger, db.ForeignKey('category.id'),
                                    nullable=False)
            category = db.relationship('Category', back_populates='posts')

    Customizing all the things::

        class Post(db.Model):
            _category_id = db.foreign_key('category_id',  # db column name
                                          db.String,      # db column type
                                          'categories',   # foreign table name
                                          fk_col='pk')    # foreign key col name

    Is equivalent to::

        class Post(db.Model):
            _category_id = db.Column('category_id',
                                     db.String,
                                     db.ForeignKey('categories.pk'),
                                     nullable=False)

    :param args: :func:`foreign_key` takes up to three positional arguments.
    Most commonly, you will only pass one argument, which should be the model
    name, the model class, or table name you're linking to.
    If you want to customize the column name the foreign key gets stored in
    the database under, then *it must be the first string argument*, and you must
    *also* supply the model name, class or table name. You can also customize the
    column type (eg ``sa.Integer`` or ``sa.String(36)``) by passing it as an arg.

    :param str fk_col: The column name of the primary key on the *opposite* side
      of the relationship (defaults to
      :attr:`sqlalchemy_unchained._ModelRegistry.default_primary_key_column`).
    :param bool primary_key: Whether or not this :class:`~sqlalchemy.Column` is
                             a primary key.
    :param bool nullable: Whether or not this :class:`~sqlalchemy.Column` should
                          be nullable.
    :param kwargs: Any other kwargs to pass the :class:`~sqlalchemy.Column`
                   constructor.
    """
    return Column(*_get_fk_col_args(args, fk_col, _default_col_type=BigInteger),
                  primary_key=primary_key, nullable=nullable, **kwargs)
