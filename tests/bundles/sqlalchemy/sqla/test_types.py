import pytest

from dateutil import tz
from datetime import datetime, timezone
from flask_unchained.bundles.sqlalchemy.sqla import types


class TestDateTime:
    def test_process_bind_param_converts_to_utc(self):
        dt = datetime(2000, 1, 1, tzinfo=tz.gettz('America/New_York'))
        value = types.DateTime().process_bind_param(dt)
        assert dt == value
        assert value.tzinfo == timezone.utc

    def test_process_bind_param_requires_timezone_aware_dt(self):
        dt = datetime(2000, 1, 1)
        with pytest.raises(ValueError) as e:
            types.DateTime().process_bind_param(dt)
        assert 'Cannot persist timezone-naive datetime' in str(e)

    def test_process_result_value(self):
        dt = datetime(2000, 1, 1, tzinfo=timezone.utc)
        value = types.DateTime().process_result_value(dt)
        assert dt == value
        assert value.tzinfo == timezone.utc

    def test_process_result_value_as_utc(self):
        dt = datetime(2000, 1, 1, tzinfo=tz.gettz('America/New_York'))
        value = types.DateTime().process_result_value(dt)
        assert dt == value
        assert value.tzinfo == timezone.utc
