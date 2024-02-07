import factory

from flask_unchained import unchained, injectable

from .services import SessionManager


class ModelFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    @unchained.inject("session_manager")
    def _create(
        cls, model_class, *args, session_manager: SessionManager = injectable, **kwargs
    ):
        # make sure we get the correct mapped class
        model_class = unchained.sqlalchemy_bundle.models[model_class.__name__]

        # try to query for existing by primary key or unique column(s)
        filter_kwargs = {}
        for col in model_class.__mapper__.columns:
            if col.name in kwargs and (col.primary_key or col.unique):
                filter_kwargs[col.name] = kwargs[col.name]

        # otherwise try by all simple type values
        if not filter_kwargs:
            filter_kwargs = {
                k: v
                for k, v in kwargs.items()
                if "__" not in k
                and (v is None or isinstance(v, (bool, int, str, float)))
            }

        instance = (
            model_class.query.filter_by(**filter_kwargs).one_or_none()
            if filter_kwargs
            else None
        )

        if not instance:
            instance = model_class(*args, **kwargs)
            session_manager.save(instance, commit=True)
        return instance
