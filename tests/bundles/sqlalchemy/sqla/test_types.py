import pytest

from dateutil import tz
from datetime import datetime, timezone
from flask_unchained.bundles.sqlalchemy.sqla import types
from tests.bundles.sqlalchemy.conftest import POSTGRES

year, month, day, hour = 2000, 1, 1, 1


class TestDateTime:
    def test_process_bind_param_converts_to_utc(self):
        dt = datetime(year, month, day, hour, tzinfo=tz.gettz('America/New_York'))
        value = types.DateTime().process_bind_param(dt)
        assert dt == value
        assert value.tzinfo == timezone.utc

    def test_process_bind_param_requires_timezone_aware_dt(self):
        dt = datetime(year, month, day, hour)
        with pytest.raises(ValueError) as e:
            types.DateTime().process_bind_param(dt)
        assert 'Cannot persist timezone-naive datetime' in str(e)

    def test_process_result_value(self):
        dt = datetime(year, month, day, hour, tzinfo=timezone.utc)
        value = types.DateTime().process_result_value(dt)
        assert dt == value
        assert value.tzinfo == timezone.utc

    def test_process_result_value_as_utc(self):
        dt = datetime(year, month, day, hour, tzinfo=tz.gettz('America/New_York'))
        value = types.DateTime().process_result_value(dt)
        assert dt == value
        assert value.tzinfo == timezone.utc

    def test_persist_dt_sqlite(self, db, session_manager):
        self._do_persist_dt(db, session_manager)

    @pytest.mark.options(SQLALCHEMY_DATABASE_URI=POSTGRES)
    def test_persist_dt_postgres(self, db, session_manager):
        self._do_persist_dt(db, session_manager)

    def _do_persist_dt(self, db, session_manager):
        class Timestamp(db.Model):
            dt = db.Column(db.DateTime)

        db.create_all()

        instance = Timestamp(dt=datetime(year, month, day, hour,
                                         tzinfo=tz.gettz('America/New_York')))
        session_manager.save(instance, commit=True)

        queried = Timestamp.query.first()
        assert instance == queried
        assert queried.dt.tzinfo == timezone.utc
