import datetime
import pytest

from flask_unchained.utils import get_boolean_env, safe_import_module, utcnow


def test_get_boolean_env(monkeypatch):
    for truthy in ['TRUE', 'YES', 'True', 'Yes', 'true', 'yes', 'Y', 'y', '1']:
        monkeypatch.setenv('MY_ENV', truthy)
        assert get_boolean_env('MY_ENV', False) is True
        monkeypatch.undo()

    for falsy in ['any', 'THING', 'else', 'should', 'be', 'false', 'FALSE',
                  'F', 'N', 'n', '0', '']:
        monkeypatch.setenv('MY_ENV', falsy)
        assert get_boolean_env('MY_ENV', True) is False
        monkeypatch.undo()


def test_safe_import_module():
    assert safe_import_module('gobblygook') is None

    with pytest.raises(ModuleNotFoundError) as e:
        safe_import_module('should.not.exist')
    assert "No module named 'should'" in str(e)

    module = safe_import_module('flask_unchained')
    assert module.__name__ == 'flask_unchained'


def test_utc_now():
    assert utcnow().tzinfo == datetime.timezone.utc
    with pytest.raises(TypeError) as e:
        assert utcnow() <= datetime.datetime.utcnow()
    assert "can't compare offset-naive and offset-aware datetimes" in str(e)
