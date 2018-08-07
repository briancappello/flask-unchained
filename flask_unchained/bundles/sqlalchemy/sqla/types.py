import datetime as dt

from sqlalchemy import types
from sqlalchemy.dialects import sqlite


class BigInteger(types.TypeDecorator):
    impl = types.BigInteger().with_variant(sqlite.INTEGER(), 'sqlite')

    @property
    def python_type(self):
        return int

    def __repr__(self):
        return 'BigInteger()'


class DateTime(types.TypeDecorator):
    impl = types.DateTime

    def __init__(self, timezone=True):
        super().__init__(timezone=True)  # force timezone always True

    def process_bind_param(self, value, dialect=None):
        if value is not None:
            if value.tzinfo is None:
                raise ValueError('Cannot persist timezone-naive datetime')
            return value.astimezone(dt.timezone.utc)

    def process_result_value(self, value, dialect=None):
        if not value:
            return
        if not value.tzinfo:
            return value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(tz=dt.timezone.utc)

    @property
    def python_type(self):
        return dt.datetime
