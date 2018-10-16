from .base_model import QueryableBaseModel
from ...unchained import unchained, injectable


class AntiPatternBaseModel(QueryableBaseModel):
    @unchained.inject('db')
    def __init__(self, db=injectable, **kwargs):
        self.db = db
        super().__init__(**kwargs)

    def save(self, commit=False):
        self.db.session.add(self)
        if commit:
            self.db.session.commit()

    def update(self, commit=False, partial_validation=True, **kwargs):
        super().update(partial_validation=partial_validation, **kwargs)
        self.save(commit=commit)
