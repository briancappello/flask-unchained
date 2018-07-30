from flask_session import (
    SqlAlchemySessionInterface as BaseSqlAlchemySessionInterface)

try:
    from sqlalchemy import types
except ImportError:
    types = None


class SqlAlchemySessionInterface(BaseSqlAlchemySessionInterface):
    def __init__(self, db, table, key_prefix, use_signer=False,
                 permanent=True, model_class=None):
        self.db = db
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent

        if model_class is not None:
            self.sql_session_model = model_class
            return

        class Session(db.Model):
            __tablename__ = table

            id = db.Column(db.Integer, primary_key=True)
            session_id = db.Column(db.String(255), unique=True)
            data = db.Column(db.LargeBinary)
            expiry = db.Column(types.DateTime, nullable=True)

            def __init__(self, session_id, data, expiry):
                self.session_id = session_id
                self.data = data
                self.expiry = expiry

            def __repr__(self):
                return '<Session data %s>' % self.data

        self.sql_session_model = Session
