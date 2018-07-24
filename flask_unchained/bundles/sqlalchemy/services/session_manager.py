from flask_unchained import BaseService, injectable
from typing import *

from ..base_model import BaseModel as Model
from ..extensions import SQLAlchemy


class SessionManager(BaseService):
    def __init__(self, db: SQLAlchemy = injectable):
        self.db = db

    def save(self, instance: Model, commit: bool = False):
        self.db.session.add(instance)
        if commit:
            self.commit()

    def save_all(self, instances: List[Model], commit: bool = False):
        self.db.session.add_all(instances)
        if commit:
            self.commit()

    def delete(self, instance: Model, commit: bool = False):
        self.db.session.delete(instance)
        if commit:
            self.commit()

    def commit(self):
        self.db.session.commit()

    def __getattr__(self, method_name):
        return getattr(self.db.session, method_name)
