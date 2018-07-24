from flask_sqlalchemy import BaseQuery as FlaskSQLAlchemyBaseQuery


class BaseQuery(FlaskSQLAlchemyBaseQuery):
    def get(self, id):
        if isinstance(id, tuple):
            return super().get(id)
        return super().get(int(id))

    def get_by(self, **kwargs):
        return self.filter_by(**kwargs).one_or_none()
