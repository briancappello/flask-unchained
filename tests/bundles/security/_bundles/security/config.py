class TestConfig:
    TESTING = True
    SECURITY_PASSWORD_SALT = "not-secret-salt"

    SESSION_TYPE = "sqlalchemy"
