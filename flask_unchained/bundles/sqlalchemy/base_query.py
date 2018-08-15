from flask_sqlalchemy import BaseQuery as FlaskSQLAlchemyBaseQuery


class BaseQuery(FlaskSQLAlchemyBaseQuery):
    def get(self, id):
        # returns a single model by primary key id
        # triple-quote docstrings omitted so that sphinx will inherit upstream's
        if isinstance(id, tuple):
            return super().get(id)
        return super().get(int(id))

    def get_by(self, **kwargs):
        """
        Returns a single model filtering by ``kwargs``, only if a single model
        was found, otherwise it returns ``None``.

        :param kwargs: column names and their values to filter by
        :return: An instance of the model
        """
        return self.filter_by(**kwargs).one_or_none()
